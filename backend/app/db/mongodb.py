import asyncio
import datetime
import socket
from typing import Optional
import dns.resolver
from motor.motor_asyncio import AsyncIOMotorClient
from loguru import logger
from app.core.config import settings

# Configure reliable public DNS resolver (Google/Cloudflare) to bypass ISP DNS SRV lookup failures
_STATIC_DNS_FALLBACKS = {
    "github.com": "20.207.73.82",
    "api.clerk.com": "172.64.150.54",
    "api.clerk.dev": "172.64.150.54",
    "openrouter.ai": "104.18.2.115",
}
_dns_cache = {}

try:
    _custom_resolver = dns.resolver.Resolver()
    _custom_resolver.nameservers = ['8.8.8.8', '1.1.1.1', '8.8.4.4']
    _custom_resolver.timeout = 2.0
    _custom_resolver.lifetime = 3.0
    dns.resolver.default_resolver = _custom_resolver

    _orig_getaddrinfo = socket.getaddrinfo
    def _mongodb_getaddrinfo(host, port, *args, **kwargs):
        if isinstance(host, str):
            # Check fast in-memory cache first
            if host in _dns_cache:
                try:
                    return _orig_getaddrinfo(_dns_cache[host], port, *args, **kwargs)
                except Exception:
                    _dns_cache.pop(host, None)

            # Prefer fast public DNS for known external cloud services
            if any(domain in host for domain in ('mongodb.net', 'clerk.com', 'clerk.dev', 'github.com', 'openrouter.ai')):
                try:
                    answers = _custom_resolver.resolve(host, 'A')
                    if answers:
                        ip = answers[0].to_text()
                        _dns_cache[host] = ip
                        return _orig_getaddrinfo(ip, port, *args, **kwargs)
                except Exception:
                    if host in _STATIC_DNS_FALLBACKS:
                        return _orig_getaddrinfo(_STATIC_DNS_FALLBACKS[host], port, *args, **kwargs)

        try:
            return _orig_getaddrinfo(host, port, *args, **kwargs)
        except Exception:
            # Fallback to public resolver if system DNS failed (Errno 11001)
            if isinstance(host, str):
                try:
                    answers = _custom_resolver.resolve(host, 'A')
                    if answers:
                        ip = answers[0].to_text()
                        _dns_cache[host] = ip
                        return _orig_getaddrinfo(ip, port, *args, **kwargs)
                except Exception:
                    if host in _STATIC_DNS_FALLBACKS:
                        return _orig_getaddrinfo(_STATIC_DNS_FALLBACKS[host], port, *args, **kwargs)
            raise

    socket.getaddrinfo = _mongodb_getaddrinfo
except Exception as _e:
    logger.debug(f"Could not initialize custom DNS resolver for MongoDB: {_e}")


def normalize_repo_url(url: Optional[str]) -> str:
    """
    Normalizes a repository URL to ensure consistent deduplication:
    - Strips whitespace
    - Strips trailing slashes
    - Strips .git suffix (case-insensitive)
    - Returns clean base URL (e.g. 'https://github.com/owner/repo')
    """
    if not url or not isinstance(url, str):
        return ""
    u = url.strip()
    if u.lower() in ("unknown", "none", ""):
        return ""
    u = u.rstrip("/")
    if u.lower().endswith(".git"):
        u = u[:-4]
    return u


class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

    async def connect_to_mongo(self):
        logger.info(f"Connecting to MongoDB at {settings.MONGO_URI[:20]}...")
        try:
            self.client = AsyncIOMotorClient(
                settings.MONGO_URI,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000
            )
            self.db = self.client[settings.MONGO_DB_NAME]
            # Verify connection with a strict 4-second timeout so it never hangs the server
            logger.info("Pinging MongoDB...")
            await asyncio.wait_for(self.client.admin.command('ping'), timeout=4.0)
            logger.info("Successfully connected to MongoDB.")
        except asyncio.TimeoutError:
            logger.warning("MongoDB ping timed out (check Atlas IP whitelist / network). Backend will run in degraded mode.")
        except Exception as e:
            logger.error(f"Could not connect to MongoDB: {str(e)}. Backend will run in degraded mode.")

    async def close_mongo_connection(self):
        logger.info("Closing MongoDB connection...")
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed.")

    async def verify_connection(self):
        try:
            await self.client.admin.command('ping')
            return True
        except Exception:
            return False

    async def store_user_data(self, user_data: dict):
        if self.db is None:
            await self.connect_to_mongo()
        
        try:
            result = await self.db.users.update_one(
                {"clerk_id": user_data.get("clerk_id")},
                {"$set": {**user_data, "updated_at": datetime.datetime.now()}},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Error storing user data: {e}")
            return False

    async def store_deployment_data(self, deployment_data: dict):
        """
        Stores or updates deployment data in MongoDB.
        If a repository was previously tested (e.g., failed and re-tested to success),
        this updates the existing deployment record for that repository rather than
        creating duplicate records.
        """
        if self.db is None:
            await self.connect_to_mongo()
        
        try:
            import re
            data = deployment_data.copy()
            # Clean up non-serializable objects (like datetime)
            if "start_time" in data and isinstance(data["start_time"], datetime.datetime):
                data["start_time"] = data["start_time"].isoformat()

            task_id = data.get("id") or data.get("task_id")
            repo_url = data.get("repo_url")
            user_id = data.get("user_id")
            clean_url = normalize_repo_url(repo_url)
            norm_key = clean_url.lower() if clean_url else ""

            if norm_key:
                data["normalized_repo_url"] = norm_key

            # Find existing deployment for this repo or task_id
            existing_doc = None

            # 1. First, check if a document exists with this task ID or previous task IDs
            if task_id:
                existing_doc = await self.db.deployments.find_one({
                    "$or": [
                        {"id": task_id},
                        {"task_id": task_id},
                        {"previous_task_ids": task_id}
                    ]
                })

            # 2. If not found by ID, match by repository URL so re-tests update the same record
            if not existing_doc and clean_url:
                regex_pattern = f"^{re.escape(clean_url)}(\\.git)?/?$"
                repo_filter = {
                    "$or": [
                        {"normalized_repo_url": norm_key},
                        {"repo_url": {"$regex": regex_pattern, "$options": "i"}}
                    ]
                }
                
                # If user_id is provided, match user's repo record first
                if user_id and user_id not in ("anonymous", "None", ""):
                    existing_doc = await self.db.deployments.find_one({
                        **repo_filter,
                        "user_id": user_id
                    })
                
                # Fallback to general repo match if not found by user_id
                if not existing_doc:
                    existing_doc = await self.db.deployments.find_one(repo_filter)

            now = datetime.datetime.now()

            if existing_doc:
                # Update existing deployment record in-place
                old_id = existing_doc.get("id")
                update_set = {
                    **data,
                    "updated_at": now
                }
                if task_id:
                    update_set["id"] = task_id
                if norm_key:
                    update_set["normalized_repo_url"] = norm_key

                update_ops = {"$set": update_set}
                
                # Keep historical task IDs so queries by any previous task_id resolve
                if old_id and old_id != task_id:
                    update_ops["$addToSet"] = {"previous_task_ids": old_id}

                await self.db.deployments.update_one(
                    {"_id": existing_doc["_id"]},
                    update_ops
                )
                logger.info(
                    f"Updated existing deployment record for repo '{clean_url}' "
                    f"(status: {data.get('status')})"
                )
            else:
                # First time deploying this repo — create new record
                update_set = {
                    **data,
                    "updated_at": now
                }
                if task_id:
                    update_set["id"] = task_id
                if norm_key:
                    update_set["normalized_repo_url"] = norm_key
                
                created_at_val = update_set.pop("created_at", None) or now.isoformat()
                upsert_query = {"id": task_id} if task_id else {"normalized_repo_url": norm_key}
                await self.db.deployments.update_one(
                    upsert_query,
                    {
                        "$set": update_set,
                        "$setOnInsert": {
                            "created_at": created_at_val
                        }
                    },
                    upsert=True
                )
                logger.info(
                    f"Created new deployment record for repo '{clean_url}' (task_id: {task_id})"
                )

            return True
        except Exception as e:
            logger.error(f"Error storing deployment data: {e}")
            return False

    async def get_deployment_by_id(self, task_id: str) -> Optional[dict]:
        """
        Fetch a single deployment record from MongoDB by task ID (or previous task ID).
        Used as a fallback when the task is no longer in the in-memory
        task_manager (e.g. after a server reload mid-deployment).
        """
        if self.db is None:
            await self.connect_to_mongo()
        try:
            doc = await self.db.deployments.find_one({
                "$or": [
                    {"id": task_id},
                    {"task_id": task_id},
                    {"previous_task_ids": task_id}
                ]
            })
            if doc:
                doc.pop("_id", None)   # strip non-serializable ObjectId
                return doc
            return None
        except Exception as e:
            logger.error(f"Error fetching deployment {task_id} from MongoDB: {e}")
            return None

    async def list_deployments(self, user_id: Optional[str] = None, limit: int = 50) -> list:
        """
        Fetches the recent deployment records from MongoDB.
        """
        if self.db is None:
            await self.connect_to_mongo()
        try:
            query = {}
            if user_id and user_id not in ("anonymous", "None", ""):
                query["user_id"] = user_id
            cursor = self.db.deployments.find(query).sort("updated_at", -1).limit(limit)
            docs = []
            async for doc in cursor:
                doc["_id"] = str(doc["_id"])
                docs.append(doc)
            return docs
        except Exception as e:
            logger.error(f"Error listing deployments from MongoDB: {e}")
            return []

    async def get_deployment_stats(self, user_id: Optional[str] = None) -> dict:
        if self.db is None:
            await self.connect_to_mongo()
            
        try:
            query = {}
            if user_id:
                query["user_id"] = user_id

            success = await self.db.deployments.count_documents({**query, "status": "success"})
            failed = await self.db.deployments.count_documents({**query, "status": "failed"})
            running = await self.db.deployments.count_documents({**query, "status": "running"})
            total = await self.db.deployments.count_documents(query)
            
            return {
                "success": success,
                "failed": failed,
                "running": running,
                "total": total
            }
        except Exception as e:
            logger.error(f"Error getting deployment stats for user {user_id}: {e}")
            return {"success": 0, "failed": 0, "running": 0, "total": 0}

db = MongoDB()

async def get_database():
    return db.db

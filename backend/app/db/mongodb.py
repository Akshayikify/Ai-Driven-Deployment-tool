from motor.motor_asyncio import AsyncIOMotorClient
from loguru import logger
from app.core.config import settings
import datetime
from typing import Optional

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

    async def connect_to_mongo(self):
        logger.info("Connecting to MongoDB...")
        try:
            self.client = AsyncIOMotorClient(settings.MONGO_URI)
            self.db = self.client[settings.MONGO_DB_NAME]
            # Verify connection
            await self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB.")
        except Exception as e:
            logger.error(f"Could not connect to MongoDB: {e}")
            raise e

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
        if self.db is None:
            await self.connect_to_mongo()
        
        try:
            # Upsert by ID to avoid duplicates
            # Copy dict so we don't modify the original (e.g. converting datetime to string)
            data = deployment_data.copy()
            # Clean up non-serializable objects (like datetime)
            if "start_time" in data and isinstance(data["start_time"], datetime.datetime):
                data["start_time"] = data["start_time"].isoformat()

            result = await self.db.deployments.update_one(
                {"id": data["id"]},
                {"$set": {**data, "updated_at": datetime.datetime.now()}},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Error storing deployment data: {e}")
            return False

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

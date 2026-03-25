from motor.motor_asyncio import AsyncIOMotorClient
from loguru import logger
from app.core.config import settings

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
        if not self.db:
            await self.connect_to_mongo()
        
        try:
            result = await self.db.users.update_one(
                {"email": user_data["email"]},
                {"$set": {**user_data, "updated_at": "2026-03-25"}},
                upsert=True
            )
            return str(result.upserted_id if result.upserted_id else "modified")
        except Exception as e:
            logger.error(f"Error storing user data: {e}")
            raise e

db = MongoDB()

async def get_database():
    return db.db

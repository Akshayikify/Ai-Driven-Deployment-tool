import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

async def test_connection():
    load_dotenv()
    uri = os.getenv("MONGO_URI")
    db_name = os.getenv("MONGO_DB_NAME", "ai_deployment_tool")
    
    print(f"Testing connection to {uri}...")
    try:
        client = AsyncIOMotorClient(uri)
        print("Pinging...")
        await client.admin.command('ping')
        print("Ping successful!")
        db = client[db_name]
        print(f"Connected to database: {db_name}")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())

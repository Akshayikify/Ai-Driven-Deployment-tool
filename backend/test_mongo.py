import asyncio
from app.db.mongodb import db

async def test_connection():
    print("Testing connection via app.db.mongodb...")
    await db.connect_to_mongo()
    if db.client:
        print("Database connected successfully!")
        # Test inserting and fetching a ping document
        res = await db.verify_connection()
        print("Database verify_connection:", res)
    else:
        print("Database connection failed.")

if __name__ == "__main__":
    asyncio.run(test_connection())


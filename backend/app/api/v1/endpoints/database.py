from fastapi import APIRouter, Depends, HTTPException
from app.db.mongodb import get_database
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

router = APIRouter()

class UserSchema(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    role: str = "user"
    created_at: datetime = datetime.utcnow()

@router.get("/status")
async def get_db_status(db: AsyncIOMotorDatabase = Depends(get_database)):
    if db is None:
        return {"connected": False, "message": "MongoDB is not connected."}
    
    try:
        # Ping the database
        await db.client.admin.command('ping')
        
        # Get some stats
        collections = await db.list_collection_names()
        
        return {
            "connected": True,
            "database_name": db.name,
            "collections": collections,
            "message": "Successfully connected to MongoDB cluster/instance."
        }
    except Exception as e:
        return {"connected": False, "message": f"Connection error: {str(e)}"}

@router.post("/seed-test-user")
async def seed_test_user(db: AsyncIOMotorDatabase = Depends(get_database)):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    test_user = {
        "username": "admin_user",
        "email": "admin@autodeploy.ai",
        "full_name": "System Administrator",
        "role": "admin",
        "created_at": datetime.utcnow()
    }
    
    try:
        # Check if user already exists
        existing_user = await db.users.find_one({"username": "admin_user"})
        if existing_user:
            return {"message": "Test user already exists in MongoDB.", "user_id": str(existing_user["_id"])}
            
        result = await db.users.insert_one(test_user)
        return {
            "message": "Test user data stored successfully in MongoDB!",
            "user_id": str(result.inserted_id)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to store user data: {str(e)}")

@router.get("/users", response_model=List[dict])
async def get_all_users(db: AsyncIOMotorDatabase = Depends(get_database)):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    users = []
    async for user in db.users.find():
        user["_id"] = str(user["_id"])  # Convert ObjectId to string
        users.append(user)
    return users

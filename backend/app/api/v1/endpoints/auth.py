from fastapi import APIRouter, Depends, HTTPException, Header
from app.db.mongodb import get_database, db as mongodb_helper
from motor.motor_asyncio import AsyncIOMotorDatabase
import httpx
from app.core.config import settings
from loguru import logger
from datetime import datetime
from typing import Optional

router = APIRouter()

@router.post("/sync-user")
async def sync_clerk_user(
    clerk_id: str, 
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Syncs user data from Clerk to MongoDB using the Clerk ID.
    This creates or updates the user record in the cluster.
    """
    if not settings.CLERK_SECRET_KEY:
        raise HTTPException(status_code=500, detail="Clerk Secret Key missing")

    # Fetch user data from Clerk API
    clerk_url = f"https://api.clerk.com/v1/users/{clerk_id}"
    headers = {"Authorization": f"Bearer {settings.CLERK_SECRET_KEY}"}

    async with httpx.AsyncClient() as client:
        response = await client.get(clerk_url, headers=headers)
        if response.status_code != 200:
            logger.error(f"Failed to fetch user from Clerk: {response.text}")
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch user data from Clerk")
        
        clerk_user = response.json()

    # Extract relevant fields
    email = next((e["email_address"] for e in clerk_user.get("email_addresses", [])), None)
    if not email:
        raise HTTPException(status_code=400, detail="User has no email address associated in Clerk")

    user_payload = {
        "clerk_id": clerk_id,
        "email": email,
        "first_name": clerk_user.get("first_name"),
        "last_name": clerk_user.get("last_name"),
        "profile_image_url": clerk_user.get("image_url"),
        "last_active_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }

    try:
        # Update or Insert user in MongoDB 'users' collection
        result = await db.users.update_one(
            {"clerk_id": clerk_id},
            {"$set": user_payload, "$setOnInsert": {"created_at": datetime.utcnow().isoformat()}},
            upsert=True
        )
        
        status = "Updated" if result.modified_count > 0 else "Created/Synced"
        logger.info(f"User {clerk_id} {status} in MongoDB cluster")
        return {"message": f"User {status} successfully in MongoDB cluster", "userId": clerk_id}
    except Exception as e:
        logger.error(f"Failed to store user in MongoDB: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhook")
async def clerk_webhook(
    payload: dict,
    # In a real app, you'd verify the svix-signature here
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Endpoint for Clerk Webhooks (recommended for production sync).
    Handles user.created and user.updated events.
    """
    event_type = payload.get("type")
    data = payload.get("data", {})
    
    if event_type in ["user.created", "user.updated"]:
        clerk_id = data.get("id")
        email = next((e["email_address"] for e in data.get("email_addresses", [])), None)
        
        user_payload = {
            "clerk_id": clerk_id,
            "email": email,
            "first_name": data.get("first_name"),
            "last_name": data.get("last_name"),
            "profile_image_url": data.get("image_url"),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        await db.users.update_one(
            {"clerk_id": clerk_id},
            {"$set": user_payload, "$setOnInsert": {"created_at": datetime.utcnow().isoformat()}},
            upsert=True
        )
        logger.info(f"Webhook processed for user: {clerk_id}")
        return {"status": "ok"}
    
    return {"status": "ignored"}

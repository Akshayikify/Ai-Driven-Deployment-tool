from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import List, Optional
from app.core.config import settings
from app.db.mongodb import get_database, db as mongodb_helper
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel

router = APIRouter()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/admin/login")

class Token(BaseModel):
    access_token: str
    token_type: str

class AdminStats(BaseModel):
    total_users: int
    total_deployments: int
    success_rate: float
    failed_rate: float
    running_deployments: int

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_admin(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None or username != settings.ADMIN_USERNAME:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return username

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username != settings.ADMIN_USERNAME or form_data.password != settings.ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/stats", response_model=AdminStats)
async def get_admin_stats(
    db: AsyncIOMotorDatabase = Depends(get_database),
    admin: str = Depends(get_current_admin)
):
    users_count = await db.users.count_documents({})
    
    stats = await mongodb_helper.get_deployment_stats() # Total stats
    
    total = stats["total"]
    success = stats["success"]
    failed = stats["failed"]
    running = stats["running"]
    
    success_rate = (success / total * 100) if total > 0 else 0
    failed_rate = (failed / total * 100) if total > 0 else 0
    
    return {
        "total_users": users_count,
        "total_deployments": total,
        "success_rate": round(success_rate, 2),
        "failed_rate": round(failed_rate, 2),
        "running_deployments": running
    }

@router.get("/users")
async def get_all_users(
    db: AsyncIOMotorDatabase = Depends(get_database),
    admin: str = Depends(get_current_admin)
):
    users = await db.users.find().to_list(100)
    # Remove MongoDB _id if it's not serializable or convert to string
    for user in users:
        user["_id"] = str(user["_id"])
    return users

@router.get("/deployments")
async def get_all_deployments(
    db: AsyncIOMotorDatabase = Depends(get_database),
    admin: str = Depends(get_current_admin)
):
    deployments = await db.deployments.find().sort("start_time", -1).to_list(100)
    for dep in deployments:
        dep["_id"] = str(dep["_id"])
    return deployments

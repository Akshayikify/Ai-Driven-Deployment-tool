import asyncio
import os
import sys

# Add backend to path
backend_path = os.path.join(os.getcwd(), "backend")
sys.path.append(backend_path)

# Manually load .env for the script
env_path = os.path.join(backend_path, ".env")
if os.path.exists(env_path):
    with open(env_path, "r") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                key, val = line.strip().split("=", 1)
                os.environ[key] = val

from app.db.mongodb import db

async def check_deployments():
    await db.connect_to_mongo()
    if db.db is None:
        print("Failed to connect to DB")
        return
        
    deployments = await db.db.deployments.find().sort("created_at", -1).to_list(10)
    if not deployments:
        print("No deployments found")
    else:
        for dep in deployments:
            print(f"ID: {dep.get('id', 'N/A')[:8]}, Language: {dep.get('language', 'N/A')}, Status: {dep.get('status', 'N/A')}")
    await db.close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(check_deployments())

from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.dependencies import get_database

router = APIRouter(tags=["/health"])

@router.get("/health")
async def health(db: AsyncIOMotorDatabase = Depends(get_database)) -> dict:
    """Проверка живости сервиса и подключения монго"""
    await db.command("ping")
    return {"status": "ok"}



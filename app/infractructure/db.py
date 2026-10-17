
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import settings

class Mongo():
    def __init__(self):
        self._client: AsyncIOMotorClient | None = None
        self._db: AsyncIOMotorDatabase | None = None
    def connect(self):
        self._client = AsyncIOMotorClient(settings.MONGO_URL)
        self._db = self._client[settings.MONGO_DB]
    def close(self):
        if self._client is not None:
            self._client.close()
        self._client = None
        self._db = None

    @property
    def db(self):
        if self._db is None:
            raise RuntimeError(
                "Mongo is not connected. Did you forget to call mongo.connect() in lifespan?"
            )
        return self._db

mongo = Mongo()
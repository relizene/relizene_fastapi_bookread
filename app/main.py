import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager


from app.api.v1 import api_router
from app.infractructure.db import mongo



@asynccontextmanager
async def lifespan(app: FastAPI):
    mongo.connect()
    yield
    mongo.close()

def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.include_router(api_router, prefix='/api/v1')
    return app

app = create_app()


if __name__ == '__main__':
    uvicorn.run('app.main:app', reload=True)





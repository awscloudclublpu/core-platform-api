from fastapi import FastAPI
import uvicorn
from contextlib import asynccontextmanager

from dotenv import load_dotenv

from db.mongo import get_mongo_client
from db.indexes import create_indexes

load_dotenv()

app = FastAPI(
    title="Horizon Backend",
    description="Backend API for Horizon 2026, hosted by AWS Cloud Club at LPU",
    version="1.0.0"
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_indexes()
    # Application startup complete
    yield # yield: control is passed to the application
    # Application starts shutting down
    client = get_mongo_client()
    await client.close()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
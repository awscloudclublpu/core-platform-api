from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from db.mongo import get_mongo_client
from db.indexes import create_indexes

from routers.auth import auth_router

load_dotenv()

openAPI_tags = [
    {
        "name": "Authentication",
        "description": "Endpoints related to user authentication and authorization.",
    }
]

app = FastAPI(
    title="Core Platform API",
    description="""
    Core Platform API is the centralized backend service that powers all current and future applications,
    websites and internal tools.

    It provides:
    - Authentication and authorization (JWT + Refresh Token)
    - Role-based access control (Attendee, Manager, Core)
    - User identity and profile management
    - Secure, reusable APIs shared accorss multiple platforms

    This API is designed to be stable, extensible and serve as the single source of truth for all platform services going forward.
    
    Goal: To reduce duplication, improve security and provide a consistent backend foundation for all products of AWS Cloud Club LPU.
    """,
    version="1.0.0",
    redoc_url="/docs/v2",
    openapi_tags=openAPI_tags,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000", "https://horizon.awslpu.in"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

registered_routers = [
    auth_router
]

for router in registered_routers:
     app.include_router(router)

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
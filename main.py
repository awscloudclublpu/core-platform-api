from fastapi import FastAPI
import uvicorn
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from db.mongo import get_mongo_client
from db.indexes import create_indexes

from routers.auth import auth_router
from routers.event import event_router
from routers.registrations import registrations_router

from core.logging.middleware import RequestLoggingMiddleware
from core.logging.trace import TraceIDMiddleware
from core.logging.transport import api_log_worker, audit_log_worker

load_dotenv()

openAPI_tags = [
    {"name": "Authentication", "description": "User authentication and authorization."},
    {"name": "Events", "description": "Event creation, updates, and metadata."},
    {"name": "Registrations", "description": "User registrations and participation in events."},
    {"name": "Attendance", "description": "Attendance tracking and analytics."},
]


@asynccontextmanager
async def lifespan(app: FastAPI):

    await create_indexes()

    asyncio.create_task(api_log_worker())
    asyncio.create_task(audit_log_worker())

    print("✅ Logging workers started")

    yield

    client = get_mongo_client()
    await client.close()
    print("🛑 MongoDB connection closed")


app = FastAPI(
    title="Core Platform API",
    description="Core Platform API is the centralized backend service powering AWS Cloud Club LPU platforms.",
    version="1.0.0",
    redoc_url="/docs/v2",
    openapi_tags=openAPI_tags,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8000",
        "https://horizon.awslpu.in",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(TraceIDMiddleware)

registered_routers = [
    auth_router,
    event_router,
    registrations_router,
]

for router in registered_routers:
    app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)
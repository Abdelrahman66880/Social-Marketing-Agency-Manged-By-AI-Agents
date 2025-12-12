from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from src.routes import drafts
from .routes import facebook, webhook, notification, schedule, analytics
from src.routes.auth import auth_router
from src.helpers.config import get_Settings
from src.helpers.logging_config import setup_logger
from src.middleware.request_logger import log_requests


get_Settings()
setup_logger()


app = FastAPI()

app.middleware("http")(log_requests)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],              # during development allow all; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_db_client():
    settings = get_Settings()
    app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    app.db_client = app.mongo_conn[settings.MONGODB_DATABASE]
    # try:
    #     await app.mongo_conn.admin.command('ping')
    #     print("✅ MongoDB connection successful")
    # except Exception as e:
    #     print("❌ MongoDB connection failed:", e)

@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongo_conn.close()

app.include_router(auth.auth_router)
app.include_router(business_info.business_info_router)
app.include_router(facebook.facebook_router)
app.include_router(drafts.draft_router)
app.include_router(webhook.webhook_router)
app.include_router(notification.notification_route)
app.include_router(schedule.schedule_router)
app.include_router(analytics.analytics_router)
app.include_router(auth_router)
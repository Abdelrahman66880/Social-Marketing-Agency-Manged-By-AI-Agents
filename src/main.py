from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from src.routes import drafts
from src.routes import facebook, webhook, notification, schedule, analytics, auth
from src.helpers.config import get_Settings
app = FastAPI()

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

@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongo_conn.close()

app.include_router(facebook.facebook_router)
app.include_router(drafts.draft_router)
app.include_router(webhook.webhook_router)
app.include_router(notification.notification_route)
app.include_router(schedule.schedule_router)
app.include_router(analytics.analytics_router)
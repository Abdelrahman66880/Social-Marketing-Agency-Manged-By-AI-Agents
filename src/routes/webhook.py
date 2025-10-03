from fastapi import APIRouter,  Request
from src.helpers.config import get_Settings


webhook_router = APIRouter(
    prefix="/webhook", 
    tags=["webhook"]
)

settings = get_Settings()
@webhook_router.get("/")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == settings.WEB_HOOK_VERIFY_TOKEN:
        return int(challenge)
    return {"error": "Verification failed"}


@webhook_router.post("/")
async def receive_message(request: Request):
    data = await request.json()
    print("Webhook event:", data)
    return {"status": "ok"}


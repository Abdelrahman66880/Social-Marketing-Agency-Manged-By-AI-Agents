from fastapi import FastAPI, Request
from src.routes import facebook
app = FastAPI()

VERIFY_TOKEN = "my_secret_123"  

app.include_router(facebook.router)

@app.get("/webhook")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return int(challenge)
    return {"error": "Verification failed"}


@app.post("/webhook")
async def receive_message(request: Request):
    data = await request.json()
    print("Webhook event:", data)
    return {"status": "ok"}
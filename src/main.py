from fastapi import FastAPI
from .routes import base, facebook
from .helpers.config import get_Settings

app = FastAPI(title="Social Marketing API")

@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI application"}
# include routers
app.include_router(base.base_router)
app.include_router(facebook.facebook_router)

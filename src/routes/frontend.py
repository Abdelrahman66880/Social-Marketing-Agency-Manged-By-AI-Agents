from fastapi import APIRouter
from fastapi.responses import FileResponse, RedirectResponse

frontend_router = APIRouter(tags=["Frontend"])

@frontend_router.get("/")
async def root():
    return RedirectResponse(url="/login")

@frontend_router.get("/login")
async def login_page():
    return FileResponse("frontend/templates/login.html")

@frontend_router.get("/dashboard.html")
async def dashboard_page():
    return FileResponse("frontend/templates/dashboard.html")

@frontend_router.get("/analytics.html")
async def analytics_page():
    return FileResponse("frontend/templates/analytics.html")
    
@frontend_router.get("/schedule.html")
async def schedule_page():
    return FileResponse("frontend/templates/schedule.html")

@frontend_router.get("/business_setup.html")
async def business_setup_page():
    return FileResponse("frontend/templates/business_setup.html")

@frontend_router.get("/home.html")
async def home_page():
    return FileResponse("frontend/templates/home.html")

@frontend_router.get("/facebook_connect.html")
async def facebook_connect_page():
    return FileResponse("frontend/templates/facebook_connect.html")

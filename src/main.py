from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def base_route():
    return {"message": "Hello, World!"}
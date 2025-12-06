from fastapi import FastAPI
from dotenv import load_dotenv
import os

load_dotenv()  # load .env file
DATA_DIR = os.getenv("DATA_DIR", "./data")
LOG_DIR = os.getenv("LOG_DIR", "./logs")
PORT = int(os.getenv("APP_PORT", 8000))

from controllers.controller import router as api_router

app = FastAPI(title="Loom Backend")
app.include_router(api_router)

@app.get("/")
async def root():
    return {"message": "Server running successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
    "main:app",
    host=os.getenv("APP_HOST", "127.0.0.1"),
    port=PORT,
    reload=True
)


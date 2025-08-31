from fastapi import FastAPI
from app.routers.webhooks import router as webhooks_router
from app.routers.conversations import router as conversations_router

app = FastAPI(title="omniAI")

app.include_router(webhooks_router)
app.include_router(conversations_router)

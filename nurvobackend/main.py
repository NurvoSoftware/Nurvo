"""Nurvo Backend - FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import scenario, chat, record, score, stt

app = FastAPI(
    title="Nurvo API",
    description="護理溝通情境遊戲 MVP 後端 API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scenario.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(record.router, prefix="/api")
app.include_router(score.router, prefix="/api")
app.include_router(stt.router, prefix="/api")


@app.get("/api/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}

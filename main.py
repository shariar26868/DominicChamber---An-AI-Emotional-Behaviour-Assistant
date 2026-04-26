from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import init_db
from app.utils.exceptions import http_exception_handler
from fastapi import HTTPException

from app.routers import (
    users,
    profiles,
    questionnaire,
    guidance,
    conversations,
    ratings,
    message_rewrite,
    tasks
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Person Advisor API",
    description="AI-powered guidance on how to deal with people in your life",
    version="1.0.0",
    lifespan=lifespan
)


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
app.add_exception_handler(HTTPException, http_exception_handler)


# Routers
# app.include_router(users.router)  # DISABLED
app.include_router(profiles.router)
app.include_router(questionnaire.router)
app.include_router(guidance.router)
app.include_router(conversations.router)
app.include_router(ratings.router)
app.include_router(message_rewrite.router)
app.include_router(tasks.router)


@app.get("/")
async def root():
    return {
        "message": "Person Advisor API is running",
        "docs": "/docs",
        "version": "1.0.0"
    }
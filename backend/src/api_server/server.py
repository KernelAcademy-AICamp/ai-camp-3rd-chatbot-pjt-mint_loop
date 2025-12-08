"""FastAPI server entry point.

Trip Kit Image Generation API - Clean Architecture
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .controllers import (
    health_router,
    generate_router,
    chat_router,
    recommendation_router,
)

settings = get_settings()

app = FastAPI(
    title="Trip Kit Image Generation API",
    description="AI-powered travel image generation with vibe-driven aesthetics",
    version="2.2.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health_router)
app.include_router(generate_router)
app.include_router(chat_router)
app.include_router(recommendation_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

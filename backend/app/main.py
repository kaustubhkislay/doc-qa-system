import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import documents, query
from app.models.schemas import HealthResponse

app = FastAPI(
    title="Document Q&A API",
    description="Ask questions about your PDF documents using AI",
    version="1.0.0"
)

# CORS configuration - read from environment for production
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173")
origins = [origin.strip() for origin in allowed_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(documents.router)
app.include_router(query.router)


@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint."""
    return HealthResponse(status="healthy")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="healthy")
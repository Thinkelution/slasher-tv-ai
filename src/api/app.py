"""
FastAPI Application for Slasher TV AI
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Slasher TV AI",
    description="API for generating motorcycle promo videos",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routes
from .routes import router
app.include_router(router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "Slasher TV AI API", "status": "running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


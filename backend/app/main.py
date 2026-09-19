import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine
from app.routers import auth_router, scrap_router, recycler_router, matching_router, admin_router

# Initialize Database Schema
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Kabadiwala Connect API",
    description="Smart India Hackathon 2026 - Formalizing Informal Waste Collectors",
    version="1.0.0"
)

# Enable CORS for Flutter Client
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static Files for Uploaded Images
os.makedirs("static/uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include API Routers
app.include_router(auth_router.router, prefix="/auth", tags=["Authentication"])
app.include_router(scrap_router.router, prefix="/scrap", tags=["Collector / Scrap"])
app.include_router(recycler_router.router, prefix="/recyclers", tags=["Recyclers & Offers"])
app.include_router(matching_router.router, prefix="/matching", tags=["ML & Matching Engine"])
app.include_router(admin_router.router, prefix="/admin", tags=["Admin Portal"])

@app.get("/")
def root():
    return {
        "status": "online",
        "project": "Kabadiwala Connect",
        "hackathon": "Smart India Hackathon 2026",
        "problem_statement": "SIH26229"
    }

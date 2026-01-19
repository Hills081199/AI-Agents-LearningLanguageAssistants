import os
import sys

# Add current directory to path for imports when running directly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, sessions, history

app = FastAPI(
    title="Language Learning Auth Service",
    description="Authentication and CRUD service for Language Learning App",
    version="1.0.0"
)

# CORS middleware - allow all origins for flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(sessions.router)
app.include_router(history.router)


@app.get("/")
def root():
    return {
        "service": "Language Learning Auth Service",
        "version": "1.0.0",
        "endpoints": {
            "auth": "/auth",
            "sessions": "/sessions",
            "lesson_history": "/lesson-history"
        }
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "auth_service"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

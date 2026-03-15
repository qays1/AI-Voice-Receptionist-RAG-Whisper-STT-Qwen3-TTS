from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .api.endpoints import router as api_router
from .core.config import settings
from .core.db import init_db

app = FastAPI(title=settings.APP_NAME)

@app.on_event("startup")
def on_startup():
    init_db()

# CORS middleware for frontend interaction
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for audio playback
app.mount("/audio", StaticFiles(directory="backend/data/tts_output"), name="audio")

# Serve Frontend
app.mount("/static", StaticFiles(directory="frontend"), name="static")

from fastapi.responses import RedirectResponse
@app.get("/")
async def root():
    return RedirectResponse(url="/static/landing.html")

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

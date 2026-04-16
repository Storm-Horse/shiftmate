import os
import logging
from fastapi import FastAPI

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .database import engine, Base
from . import models  # register ORM models
from .routes import auth, users, shifts, timesheets
from .migrations import run as run_migrations

# Ensure data directory exists (for persistent volume in production)
os.makedirs("/data", exist_ok=True)

Base.metadata.create_all(bind=engine)  # creates new tables
run_migrations(engine)                 # adds any new columns to existing tables

app = FastAPI(title="ShiftMate API", version="1.0.0", docs_url="/api/docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:4173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(shifts.router, prefix="/api/v1")
app.include_router(timesheets.router, prefix="/api/v1")


@app.get("/api/v1/health")
def health():
    return {"status": "ok"}


# Serve React frontend (production build)
_static = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.isdir(_static):
    app.mount("/assets", StaticFiles(directory=os.path.join(_static, "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_spa(full_path: str):
        """Catch-all: serve index.html for any non-API route (React Router)."""
        return FileResponse(os.path.join(_static, "index.html"))

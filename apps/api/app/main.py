from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router

app = FastAPI(title="Workout Logger Planner")
app.include_router(api_router)

static_dir = Path(__file__).resolve().parent / "static"
assets_dir = static_dir / "assets"

if assets_dir.exists():
    app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/{path:path}", response_model=None)
def spa(path: str):
    index_path = static_dir / "index.html"
    if index_path.exists() and not path.startswith("api/"):
        return FileResponse(index_path)
    return {"message": "Frontend not built yet"}

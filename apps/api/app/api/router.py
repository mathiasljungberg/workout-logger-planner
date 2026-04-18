from fastapi import APIRouter

from app.api.routes import analytics, auth, blocks, exercises, planned_workouts, sessions, templates

api_router = APIRouter(prefix="/api")
api_router.include_router(auth.router)
api_router.include_router(exercises.router)
api_router.include_router(templates.router)
api_router.include_router(blocks.router)
api_router.include_router(planned_workouts.router)
api_router.include_router(sessions.router)
api_router.include_router(analytics.router)


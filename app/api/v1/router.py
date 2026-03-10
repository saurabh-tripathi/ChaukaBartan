from fastapi import APIRouter

from app.api.v1 import dashboard, goals, habits, plans, tasks

router = APIRouter(prefix="/api/v1")

router.include_router(goals.router)
router.include_router(tasks.router)
router.include_router(habits.router)
router.include_router(plans.router)
router.include_router(dashboard.router)

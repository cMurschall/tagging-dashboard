from fastapi import APIRouter

from . import playerController, projectController

router = APIRouter()

playerController = playerController.PlayerController()
projectController = projectController.ProjectController()

# Include endpoints
router.include_router(playerController.router, prefix="/player", tags=["player Endpoint"])
router.include_router(projectController.router, prefix="/project", tags=["project Endpoint"])

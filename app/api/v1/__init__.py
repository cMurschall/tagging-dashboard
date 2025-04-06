from fastapi import APIRouter

from . import playerController, projectController, tagController

router = APIRouter()

playerController = playerController.PlayerController()
projectController = projectController.ProjectController()
tagController = tagController.TagController()

# Include endpoints
router.include_router(playerController.router, prefix="/player", tags=["player Endpoint"])
router.include_router(projectController.router, prefix="/project", tags=["project Endpoint"])
router.include_router(tagController.router, prefix="/tag", tags=["tag Endpoint"])

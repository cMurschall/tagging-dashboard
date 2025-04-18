from fastapi import APIRouter

from . import playerController, projectController, tagController, webSockets

router = APIRouter()

playerController = playerController.PlayerController()
projectController = projectController.ProjectController()
tagController = tagController.TagController()

websocketController = webSockets.WebSockets()

# Include endpoints
router.include_router(playerController.router, prefix="/player", tags=["player Endpoint"])
router.include_router(projectController.router, prefix="/project", tags=["project Endpoint"])
router.include_router(tagController.router, prefix="/tag", tags=["tag Endpoint"])

router.include_router(websocketController.router, prefix="/ws", tags=["Websocket"])

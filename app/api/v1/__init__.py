from fastapi import APIRouter

from . import playerController, measurementController, projectController

router = APIRouter()

playerController = playerController.PlayerController()
measurementController = measurementController.MeasurementController()
projectController = projectController.ProjectController()

# Include endpoints
router.include_router(playerController.router, prefix="/player", tags=["player Endpoint"])
router.include_router(measurementController.router, prefix="/measurement", tags=["measurement Endpoint"])
router.include_router(projectController.router, prefix="/project", tags=["project Endpoint"])

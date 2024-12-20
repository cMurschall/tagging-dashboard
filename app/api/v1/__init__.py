from fastapi import APIRouter

from . import playerController, measurementController, taggingController

router = APIRouter()

playerController = playerController.PlayerController()
measurementController = measurementController.MeasurementController()
taggingController = taggingController.TaggingController()

# Include endpoints
router.include_router(playerController.router, prefix="/player", tags=["player Endpoint"])
router.include_router(measurementController.router, prefix="/measurement", tags=["measurement Endpoint"])
router.include_router(taggingController.router, prefix="/tagging", tags=["tagging Endpoint"])

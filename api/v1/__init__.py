from fastapi import APIRouter
from . import playerEndpoint

router = APIRouter()



# Include endpoints
router.include_router(playerEndpoint.router, prefix="/player", tags=["playerEndpoint"])

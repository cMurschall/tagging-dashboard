from fastapi import APIRouter
from . import playerEndpoint

router = APIRouter()

print("api/v1/__init__.py")
print(playerEndpoint.router)


# Include endpoints
router.include_router(playerEndpoint.router, prefix="/player", tags=["playerEndpoint"])

from datetime import datetime, timezone

import psutil
from fastapi import APIRouter

# Track service start time
start_time = datetime.now(timezone.utc)

# Shared router for global endpoints
router = APIRouter()


@router.get("/healthcheck", tags=["Healthcheck"])
async def healthcheck():
    uptime = datetime.now(timezone.utc) - start_time
    return {
        "status": "healthy",
        "uptime": str(uptime),
        "memory_usage": psutil.virtual_memory().percent,
        "cpu_usage": psutil.cpu_percent(interval=0.1)
    }

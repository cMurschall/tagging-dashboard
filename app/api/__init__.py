from datetime import datetime, timezone

import psutil
from fastapi import APIRouter
from pydantic import BaseModel

# Track service start time
start_time = datetime.now(timezone.utc)

# Shared router for global endpoints
router = APIRouter()


class HealthCheckResponse(BaseModel):
    status: str
    uptime: str
    memory_usage: float
    cpu_usage: float


@router.get("/healthcheck", tags=["Healthcheck"])
async def healthcheck() -> HealthCheckResponse:
    uptime = datetime.now(timezone.utc) - start_time
    return HealthCheckResponse(
        status="healthy",
        uptime=str(uptime),
        memory_usage=psutil.virtual_memory().percent,
        cpu_usage=psutil.cpu_percent(interval=0.1))

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def read_data():
    return {"message": "Player endpoint - Get data"}


@router.post("/")
async def create_data():
    return {"message": "Player endpoint - Create data"}

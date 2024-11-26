from fastapi import APIRouter
class MeasurementController:
    def __init__(self):
        self.router = APIRouter()
        self._define_routes()

    def _define_routes(self):
        @self.router.get("/")
        async def read_data():
            return {"message": "Measurement endpoint - Get data"}

        @self.router.post("/")
        async def create_data():
            return {"message": "Measurement endpoint - Create data"}

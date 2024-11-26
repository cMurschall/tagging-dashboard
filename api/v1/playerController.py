from fastapi import APIRouter

router = APIRouter()


class PlayerController:
    def __init__(self):
        self.router = APIRouter()
        self._define_routes()

    def _define_routes(self):
        @self.router.post("/play")
        async def play_stream():
            return {"message": "Player endpoint - Create data"}

        @self.router.post("/pause")
        async def pause_stream():
            return {"message": "Player endpoint - Create data"}

        @self.router.post("/pause")
        async def jump_to_time(timestamp: float):
            return {"message": "Player endpoint - Create data"}

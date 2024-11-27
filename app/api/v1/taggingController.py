from fastapi import APIRouter

router = APIRouter()


class TaggingController:
    def __init__(self):
        self.router = APIRouter()
        self._define_routes()

    def _define_routes(self):
        @self.router.get("/tags")
        async def get_tags():
            return {"message": "Tagging endpoint - Get data"}

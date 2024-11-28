from app.models.tag import Tag


class SingleTag(Tag):
    def __init__(self,time: float):
        self.time = time


from app.models.tag import Tag


class RangeTag(Tag):
    def __init__(self,min: float, max:float):
        self.min = min
        self.max = max


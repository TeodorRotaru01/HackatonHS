from typing import Tuple


class BoundingBox:
    """
    Simple Bounding Box class.
    x_min, y_min = top-left corner
    width, height = dimensions
    """

    def __init__(self, x_min: int, y_min: int, width: int, height: int):
        self.x_min = x_min
        self.y_min = y_min
        self.width = width
        self.height = height

    def __repr__(self):
        return f"BoundingBox(x={self.x_min}, y={self.y_min}, w={self.width}, h={self.height})"

    def __iter__(self):
        yield from (self.x_min, self.y_min, self.width, self.height)

    def center(self) -> Tuple[int, int]:
        """
        Returns the (x, y) center of the bounding box.
        """
        return (
            self.x_min + self.width // 2,
            self.y_min + self.height // 2
        )

    def to_tuple(self) -> Tuple[int, int, int, int]:
        return self.x_min, self.y_min, self.width, self.height

from __future__ import annotations


class Rectangle:
    def __init__(
        self, startCoordinates: tuple[int, int], endCoordinates: tuple[int, int]
    ) -> None:
        self.startCoordinates = startCoordinates
        self.endCoordinates = endCoordinates

        self.x = self.startCoordinates[0]
        self.y = self.startCoordinates[1]

        self.width = self.endCoordinates[0] - self.x
        self.height = self.endCoordinates[1] - self.y


class ColorRectange(Rectangle):
    def __init__(
        self,
        color: tuple[int, int, int],
        startCoordinates: tuple[int, int],
        endCoordinates: tuple[int, int],
    ) -> None:

        super(ColorRectange, self).__init__(startCoordinates, endCoordinates)
        self.color = color


class RectangleMatch:
    def __init__(self, x: int, y: int, data: list[tuple[int, int, int]]) -> None:
        self.x = x
        self.y = y
        self.data = data

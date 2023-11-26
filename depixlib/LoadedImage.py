from __future__ import annotations

from typing import cast
from PIL import Image


class LoadedImage:
    def __init__(self, path: str) -> None:
        self.path = path
        self.loadedImage = Image.open(self.path)
        self.width = self.loadedImage.size[0]
        self.height = self.loadedImage.size[1]
        self.imageData = self.__loadImageData()

    def getCopyOfLoadedPILImage(self) -> Image.Image:
        return self.loadedImage.copy()

    def __loadImageData(self) -> list[list[tuple[int, int, int]]]:
        """Load data from image with getdata() because of the speed increase over consecutive calls to getpixel"""
        _imageData = [[y for y in range(self.height)] for x in range(self.width)]

        rawData = self.loadedImage.getdata()
        rawDataCount = 0

        # because getdata returns the image as one big list
        for y in range(self.height):
            for x in range(self.width):

                _imageData[x][y] = rawData[rawDataCount][0:3]
                rawDataCount += 1
        return cast(list[list[tuple[int, int, int]]], _imageData)

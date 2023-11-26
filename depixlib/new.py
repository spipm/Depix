




# Couldn't make sense of old code wtf
# Simply parse the image as a set of rectangles with static size
def findStaticBoxes(
    pixelatedImage: LoadedImage,
    boxSize: int,
    maxCoordinates: tuple[int, int],
) -> ColorRectange:

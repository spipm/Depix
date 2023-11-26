import argparse
import logging
import os
import shutil

from depix import DepixHelpFormatter
from LoadedImage import LoadedImage


def check_file(s: str) -> str:
    if os.path.isfile(s):
        return s
    else:
        raise argparse.ArgumentTypeError("%s is not a file." % repr(s))


def parse_args() -> argparse.Namespace:
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(
        description="This command generates pixelized image from a given image.",
        formatter_class=(
            lambda prog: DepixHelpFormatter(
                prog,
                **{
                    "width": shutil.get_terminal_size(fallback=(120, 50)).columns,
                    "max_help_position": 40,
                },
            )
        ),
    )
    parser.add_argument(
        "-i",
        "--image",
        help="path to image to pixelize",
        required=True,
        type=check_file,
        metavar="PATH",
    )
    parser.add_argument(
        "-o",
        "--outputimage",
        help="path to output image",
        default="output.png",
        metavar="PATH",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    imagePath = args.image

    image = LoadedImage(imagePath)
    outputImage = image.getCopyOfLoadedPILImage()

    blockSize = 5
    blockPixelCount = blockSize * blockSize

    for x in range(0, image.width, blockSize):
        for y in range(0, image.height, blockSize):

            r = g = b = 0

            maxX = min(x + blockSize, image.width)
            maxY = min(y + blockSize, image.height)

            for xx in range(x, maxX):
                for yy in range(y, maxY):

                    currentPixel = image.imageData[xx][yy]
                    r += currentPixel[0]
                    g += currentPixel[1]
                    b += currentPixel[2]

            averageR = int(r / blockPixelCount)
            averageG = int(g / blockPixelCount)
            averageB = int(b / blockPixelCount)
            averageColor = (averageR, averageG, averageB)

            for xx in range(x, maxX):
                for yy in range(y, maxY):

                    outputImage.putpixel((xx, yy), averageColor)

    outputImage.save(args.outputimage)


if __name__ == "__main__":
    main()

# Generated:
# 676c81
# Gimp:
# 878a9e

# diff: 2104861

# Generated:
# 889475
# Gimp:
# a7b194

# diff: 2039071

# ?

from __future__ import annotations

import argparse
import logging
logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)

from PIL import Image, ImageDraw

from depixlib.helpers import (
    check_file,
    check_color
)
from depixlib.functions import (
    dropEmptyRectangleMatches,
    findGeometricMatchesForSingleResults,
    findRectangleMatches,
    findRectangleSizeOccurences,
    findSameColorSubRectangles,
    removeMootColorRectangles,
    splitSingleMatchAndMultipleMatches,
    writeAverageMatchToImage,
    writeFirstMatchToImage
)
from depixlib.LoadedImage import LoadedImage
from depixlib.Rectangle import Rectangle


def parse_args() -> argparse.Namespace:
    
    usage = """
    note:
        The pixelated rectangle must be cut out to only include the pixelated rectangles.
        The pattern search image is generally a screenshot of a De Bruijn sequence of expected characters,
        made on a machine with the same editor and text size as the original screenshot that was pixelated.
    """

    parser = argparse.ArgumentParser(
        description="This command recovers passwords from pixelized screenshots.",
        epilog=usage
    )
    parser.add_argument(
        "-p",
        "--pixelimage",
        help="path to image with pixelated rectangle",
        required=True,
        default=argparse.SUPPRESS,
        type=check_file,
        metavar="PATH"
    )
    parser.add_argument(
        "-s",
        "--searchimage",
        help="path to image with patterns to search",
        required=True,
        default=argparse.SUPPRESS,
        type=check_file,
        metavar="PATH",
    )
    parser.add_argument(
        "-a",
        "--averagetype",
        help="type of RGB average to use",
        default="gammacorrected",
        choices=["gammacorrected", "linear"],
        metavar="TYPE",
    )
    parser.add_argument(
        "-b",
        "--backgroundcolor",
        help="original editor background color in format r,g,b (color to ignore)",
        default=None,
        type=check_color,
        metavar="RGB"
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

    pixelatedImagePath = args.pixelimage
    searchImagePath = args.searchimage
    editorBackgroundColor: tuple[int, int, int] | None = args.backgroundcolor
    averageType = args.averagetype

    logging.info("Loading pixelated image from %s" % pixelatedImagePath)
    pixelatedImage = LoadedImage(pixelatedImagePath)
    unpixelatedOutputImage = pixelatedImage.getCopyOfLoadedPILImage()

    logging.info("Loading search image from %s" % searchImagePath)
    searchImage = LoadedImage(searchImagePath)

    logging.info("Finding color rectangles from pixelated space")
    # fill coordinates here if not cut out
    pixelatedRectange = Rectangle(
        (0, 0), (pixelatedImage.width - 1, pixelatedImage.height - 1)
    )

    pixelatedSubRectanges = findSameColorSubRectangles(
        pixelatedImage, pixelatedRectange
    )
    logging.info("Found %s same color rectangles" % len(pixelatedSubRectanges))

    pixelatedSubRectanges = removeMootColorRectangles(
        pixelatedSubRectanges, editorBackgroundColor
    )
    logging.info("%s rectangles left after moot filter" % len(pixelatedSubRectanges))

    rectangeSizeOccurences = findRectangleSizeOccurences(pixelatedSubRectanges)
    logging.info("Found %s different rectangle sizes" % len(rectangeSizeOccurences))
    if len(rectangeSizeOccurences) > max(
        10, pixelatedRectange.width * pixelatedRectange.height * 0.01
    ):
        logging.warning(
            "Too many variants on block size. Re-cropping the image might help."
        )

    logging.info("Finding matches in search image")
    rectangleMatches = findRectangleMatches(
        rectangeSizeOccurences, pixelatedSubRectanges, searchImage, averageType
    )

    logging.info("Removing blocks with no matches")
    pixelatedSubRectanges = dropEmptyRectangleMatches(
        rectangleMatches, pixelatedSubRectanges
    )

    # Enhance like in the movies
    enhance = 3
    
    image = Image.open(pixelatedImagePath)
    enhancedImage = image.resize((image.width*enhance, image.height*enhance))
    draw = ImageDraw.Draw(enhancedImage)

    # Show crappy box detector output
    for box in pixelatedSubRectanges:

        draw.line([
            (box.x*enhance, box.y*enhance),
            (((box.x+box.width)*enhance)-enhance, box.y*enhance ),
            (((box.x+box.width)*enhance)-enhance, ((box.y+box.height)*enhance)-enhance),
            (box.x*enhance, ((box.y+box.height)*enhance) - enhance),
            (box.x*enhance, box.y*enhance)
            ], width=1, fill="red")

    enhancedImage.show()


if __name__ == "__main__":
    main()

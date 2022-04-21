from __future__ import annotations

import argparse
import logging
import os
import shutil
import textwrap
from typing import cast

from . import __version__
from .functions import (
    dropEmptyRectangleMatches,
    findGeometricMatchesForSingleResults,
    findRectangleMatches,
    findRectangleSizeOccurences,
    findSameColorSubRectangles,
    removeMootColorRectangles,
    splitSingleMatchAndMultipleMatches,
    writeAverageMatchToImage,
    writeFirstMatchToImage,
)
from .LoadedImage import LoadedImage
from .Rectangle import Rectangle


class DepixHelpFormatter(
    argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter
):
    pass


def check_file(s: str) -> str:
    if os.path.isfile(s):
        return s
    else:
        raise argparse.ArgumentTypeError("%s is not a file." % repr(s))


def check_color(s: str | None) -> tuple[int, int, int] | None:
    if s is None:
        return None
    ss = s.split(",")
    if len(ss) != 3:
        raise argparse.ArgumentTypeError("Given colors must be formatted as 'r,g,b'.")
    else:
        try:
            return cast(tuple[int, int, int], tuple([int(i) for i in ss]))
        except ValueError:
            raise argparse.ArgumentTypeError(
                "Maybe %s is not '<int>,<int>,<int>'." % repr(s)
            )


def parse_args() -> argparse.Namespace:
    logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)

    usage = textwrap.dedent("""
    note:
        The pixelated rectangle must be cut out to only include the pixelated rectangles.
        The pattern search image is generally a screenshot of a De Bruijn sequence of expected characters,
        made on a machine with the same editor and text size as the original screenshot that was pixelated.
    """)

    parser = argparse.ArgumentParser(
        description="This command recovers passwords from pixelized screenshots.",
        formatter_class=(
            lambda prog: DepixHelpFormatter(
                prog,
                **{
                    "width": shutil.get_terminal_size(fallback=(120, 50)).columns,
                    "max_help_position": 40,
                },
            )
        ),
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
        help="original editor background color in format r,g,b",
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
    parser.add_argument(
        "-V", "--version", action="version", version=f"%(prog)s {__version__}"
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
            "Too many variants on block size. Re-pixelating the image might help."
        )

    logging.info("Finding matches in search image")
    rectangleMatches = findRectangleMatches(
        rectangeSizeOccurences, pixelatedSubRectanges, searchImage, averageType
    )

    logging.info("Removing blocks with no matches")
    pixelatedSubRectanges = dropEmptyRectangleMatches(
        rectangleMatches, pixelatedSubRectanges
    )

    logging.info("Splitting single matches and multiple matches")
    singleResults, pixelatedSubRectanges = splitSingleMatchAndMultipleMatches(
        pixelatedSubRectanges, rectangleMatches
    )

    logging.info(
        "[%s straight matches | %s multiple matches]"
        % (len(singleResults), len(pixelatedSubRectanges))
    )

    logging.info("Trying geometrical matches on single-match squares")
    singleResults, pixelatedSubRectanges = findGeometricMatchesForSingleResults(
        singleResults, pixelatedSubRectanges, rectangleMatches
    )

    logging.info(
        "[%s straight matches | %s multiple matches]"
        % (len(singleResults), len(pixelatedSubRectanges))
    )

    logging.info("Trying another pass on geometrical matches")
    singleResults, pixelatedSubRectanges = findGeometricMatchesForSingleResults(
        singleResults, pixelatedSubRectanges, rectangleMatches
    )

    logging.info(
        "[%s straight matches | %s multiple matches]"
        % (len(singleResults), len(pixelatedSubRectanges))
    )

    logging.info("Writing single match results to output")
    writeFirstMatchToImage(
        singleResults, rectangleMatches, searchImage, unpixelatedOutputImage
    )

    logging.info("Writing average results for multiple matches to output")
    writeAverageMatchToImage(
        pixelatedSubRectanges, rectangleMatches, searchImage, unpixelatedOutputImage
    )

    # writeRandomMatchesToImage(pixelatedSubRectanges, rectangleMatches, searchImage, unpixelatedOutputImage)

    logging.info("Saving output image to: %s" % args.outputimage)
    unpixelatedOutputImage.save(args.outputimage)


if __name__ == "__main__":
    main()

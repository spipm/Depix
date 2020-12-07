from depixlib.LoadedImage import *
from depixlib.Rectangle import *
from depixlib.functions import *

import argparse
import logging
logging.basicConfig(level=logging.INFO)


usage = '''
	The pixelated rectangle must be cut out to only include the pixelated rectangles.
	The pattern search image is generally a screenshot of a De Bruijn sequence of expected characters,
	made on a machine with the same editor and text size as the original screenshot that was pixelated. 
'''

parser = argparse.ArgumentParser(description = usage)
parser.add_argument('-p', '--pixelimage', help = 'Path to image with pixelated rectangle', required=True)
parser.add_argument('-s', '--searchimage', help = 'Path to image with patterns to search', required=True)
parser.add_argument('-o', '--outputimage', help = 'Path to output image', nargs='?', default='output.png')
args = parser.parse_args()

pixelatedImagePath = args.pixelimage
searchImagePath = args.searchimage


logging.info("Loading pixelated image from %s" % pixelatedImagePath)
pixelatedImage = LoadedImage(pixelatedImagePath)
unpixelatedOutputImage = pixelatedImage.getCopyOfLoadedPILImage()

logging.info("Loading search image from %s" % searchImagePath)
searchImage = LoadedImage(searchImagePath)


logging.info("Finding color rectangles from pixelated space")
# fill coordinates here if not cut out
pixelatedRectange = Rectangle((0, 0), (pixelatedImage.width-1, pixelatedImage.height-1))


pixelatedSubRectanges = findSameColorSubRectangles(pixelatedImage, pixelatedRectange)
logging.info("Found %s same color rectangles" % len(pixelatedSubRectanges))

pixelatedSubRectanges = removeMootColorRectangles(pixelatedSubRectanges)
logging.info("%s rectangles left after moot filter" % len(pixelatedSubRectanges))

rectangeSizeOccurences = findRectangleSizeOccurences(pixelatedSubRectanges)
logging.info("Found %s different rectangle sizes" % len(rectangeSizeOccurences))

logging.info("Finding matches in search image")
rectangleMatches = findRectangleMatches(rectangeSizeOccurences, pixelatedSubRectanges, searchImage)

logging.info("Removing blocks with no matches")
pixelatedSubRectanges = dropEmptyRectangleMatches(rectangleMatches, pixelatedSubRectanges)


logging.info("Splitting single matches and multiple matches")
singleResults, pixelatedSubRectanges = splitSingleMatchAndMultipleMatches(pixelatedSubRectanges, rectangleMatches)

logging.info("[%s straight matches | %s multiple matches]" % (len(singleResults), len(pixelatedSubRectanges)))

logging.info("Trying geometrical matches on single-match squares")
singleResults, pixelatedSubRectanges = findGeometricMatchesForSingleResults(singleResults, pixelatedSubRectanges, rectangleMatches)

logging.info("[%s straight matches | %s multiple matches]" % (len(singleResults), len(pixelatedSubRectanges)))

logging.info("Trying another pass on geometrical matches")
singleResults, pixelatedSubRectanges = findGeometricMatchesForSingleResults(singleResults, pixelatedSubRectanges, rectangleMatches)

logging.info("[%s straight matches | %s multiple matches]" % (len(singleResults), len(pixelatedSubRectanges)))


logging.info("Writing single match results to output")
writeFirstMatchToImage(singleResults, rectangleMatches, searchImage, unpixelatedOutputImage)

logging.info("Writing average results for multiple matches to output")
writeAverageMatchToImage(pixelatedSubRectanges, rectangleMatches, searchImage, unpixelatedOutputImage)

# writeRandomMatchesToImage(pixelatedSubRectanges, rectangleMatches, searchImage, unpixelatedOutputImage)

logging.info("Saving output image to: %s" % args.outputimage)
unpixelatedOutputImage.save(args.outputimage)

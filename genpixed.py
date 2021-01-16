from depixlib.LoadedImage import *
from depixlib.Rectangle import *
from depixlib.functions import *

import argparse
import logging
logging.basicConfig(level=logging.INFO)


parser = argparse.ArgumentParser()
parser.add_argument('-i', '--image', help = 'Path to image to pixelize', required=True)
parser.add_argument('-o', '--outputimage', help = 'Path to output image', nargs='?', default='output.png')
args = parser.parse_args()

imagePath = args.image


image = LoadedImage(imagePath)
outputImage = image.getCopyOfLoadedPILImage()

blockSize = 5
blockPixelCount = blockSize * blockSize

for x in range(0, image.width, blockSize):
	for y in range(0, image.height, blockSize):

		r = g = b = 0

		maxX = min(x+blockSize, image.width)
		maxY = min(y+blockSize, image.height)

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

				outputImage.putpixel((xx,yy), averageColor)

outputImage.save(args.outputimage)

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




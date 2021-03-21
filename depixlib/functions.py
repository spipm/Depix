from depixlib.Rectangle import *
from random import choice
from PIL import Image
import logging
logging.basicConfig(level=logging.INFO)



def findSameColorRectangle(pixelatedImage, startCoordinates, maxCoordinates):

	startx, starty = startCoordinates
	color = pixelatedImage.imageData[startx][starty]

	width = 0
	height = 0
	maxx, maxy = maxCoordinates

	# finds width and height quick
	for x in range(startx, maxx):
		if pixelatedImage.imageData[x][starty] == color:
			width += 1
		else:
			break

	for y in range(starty,maxy):
		if pixelatedImage.imageData[startx][y] == color:
			height += 1
		else:
			break

	# checks if real rectange with same color. prefers vertical rectangles
	for testx in range(startx, startx+width):
		for testy in range(starty, starty+height):

			if pixelatedImage.imageData[testx][testy] != color:
				# logging.info("Found rectangle error")
				return ColorRectange(color, (startx, starty), (testx, testy))

	return ColorRectange(color, (startx, starty), (startx + width, starty + height))


def findSameColorSubRectangles(pixelatedImage, rectangle):

	sameColorRectanges = []

	x = rectangle.x
	maxx = rectangle.x + rectangle.width + 1
	maxy = rectangle.y + rectangle.height + 1

	while x < maxx:
		y = rectangle.y

		while y < maxy:

			sameColorRectange = findSameColorRectangle(pixelatedImage, (x, y), (maxx, maxy))
			if sameColorRectange == False:
				continue
			# logging.info("Found rectangle at (%s, %s) with size (%s,%s) and color %s" % (x, y, sameColorRectange.width,sameColorRectange.height,sameColorRectange.color))
			sameColorRectanges.append(sameColorRectange)

			y += sameColorRectange.height

		x += sameColorRectange.width

	return sameColorRectanges


def removeMootColorRectangles(colorRectanges, editorBackgroundColor):

	pixelatedSubRectanges = []

	mootColors = [(0,0,0), (255,255,255)]
	if editorBackgroundColor != None:
		mootColors.append(editorBackgroundColor)

	for colorRectange in colorRectanges:

			if colorRectange.color in mootColors:
				continue

			pixelatedSubRectanges.append(colorRectange)

	return pixelatedSubRectanges


def findRectangleSizeOccurences(colorRectanges):

	rectangeSizeOccurences = {}

	for colorRectange in colorRectanges:

		size = (colorRectange.width, colorRectange.height)

		if size in rectangeSizeOccurences:
			rectangeSizeOccurences[size] += 1
		else:
			rectangeSizeOccurences[size] = 1

	return rectangeSizeOccurences


# Thanks to Artoria2e5, see
# https://github.com/beurtschipper/Depix/pull/45
def srgb2lin(s):
    if s <= 0.0404482362771082:
        lin = s / 12.92
    else:
        lin = ((s + 0.055) / 1.055) ** 2.4
    return lin


def lin2srgb(lin):
    if lin > 0.0031308:
        s = 1.055 * lin**(1.0 / 2.4) - 0.055
    else:
        s = 12.92 * lin
    return s


# return a dictionary, with sub-rectangle coordinates as key and RectangleMatch as value
def findRectangleMatches(rectangeSizeOccurences, pixelatedSubRectanges, searchImage, averageType = 'gammacorrected'):

	rectangleMatches = {}

	for rectangeSizeOccurence in rectangeSizeOccurences:

		rectangleSize = rectangeSizeOccurence
		rectangleWidth = rectangleSize[0]
		rectangleHeight = rectangleSize[1]
		pixelsInRectangle = rectangleWidth*rectangleHeight

		# filter out the desired rectangle size
		matchingRectangles = []
		for colorRectange in pixelatedSubRectanges:

			if (colorRectange.width, colorRectange.height) == rectangleSize:
				matchingRectangles.append(colorRectange)

		logging.info('Scanning {} blocks with size {}'.format(len(matchingRectangles), rectangleSize))

		for x in range(searchImage.width - rectangleWidth):
			for y in range(searchImage.height - rectangleHeight):

				r = g = b = 0
				matchData = []

				for xx in range(rectangleWidth):

					for yy in range(rectangleHeight):

						newPixel = searchImage.imageData[x+xx][y+yy]
						matchData.append(newPixel)

						if averageType == 'gammacorrected':
							rr,gg,bb = newPixel
						
						if averageType == 'linear':
							newPixelLinear = tuple(srgb2lin(v/255) for v in newPixel)
							rr,gg,bb = newPixelLinear

						r += rr
						g += gg
						b += bb

				if averageType == 'gammacorrected':
					averageColor = (int(r / pixelsInRectangle), int(g / pixelsInRectangle), int(b / pixelsInRectangle))

				elif averageType == 'linear':
					averageColor = tuple(int(round(lin2srgb(v / pixelsInRectangle)*255)) for v in (r,g,b))

				for matchingRectangle in matchingRectangles:

					if (matchingRectangle.x,matchingRectangle.y) not in rectangleMatches:
						rectangleMatches[(matchingRectangle.x,matchingRectangle.y)] = []

					if matchingRectangle.color == averageColor:
						newRectangleMatch = RectangleMatch(x, y, matchData)
						rectangleMatches[(matchingRectangle.x,matchingRectangle.y)].append(newRectangleMatch)

			if x % 64 == 0:
				logging.info('Scanning in searchImage: {}/{}'.format(x, searchImage.width - rectangleWidth))

	return rectangleMatches


def dropEmptyRectangleMatches(rectangleMatches, pixelatedSubRectanges):

	newPixelatedSubRectanges = []
	for pixelatedSubRectange in pixelatedSubRectanges:

		if len(rectangleMatches[(pixelatedSubRectange.x,pixelatedSubRectange.y)]) > 0:
			newPixelatedSubRectanges.append(pixelatedSubRectange)

	return newPixelatedSubRectanges


def splitSingleMatchAndMultipleMatches(pixelatedSubRectanges, rectangleMatches):

	newPixelatedSubRectanges = []
	singleResults = []
	for colorRectange in pixelatedSubRectanges:

		firstMatchData = rectangleMatches[(colorRectange.x,colorRectange.y)][0].data
		singleMatch = True   # only one data matches

		for match in rectangleMatches[(colorRectange.x,colorRectange.y)]:

			if firstMatchData != match.data:
				singleMatch = False
				break

		if singleMatch:
			singleResults.append(colorRectange)
		else:
			newPixelatedSubRectanges.append(colorRectange)

	return singleResults, newPixelatedSubRectanges


def isNeighbor(pixelA, pixelB):
	return (pixelA.x - pixelB.x) in [pixelB.width, 0, -pixelA.width] \
		and (pixelA.y - pixelB.y) in [pixelB.height, 0, -pixelA.height] \
		and pixelA != pixelB


def findGeometricMatchesForSingleResults(singleResults, pixelatedSubRectanges, rectangleMatches):

	newPixelatedSubRectanges = pixelatedSubRectanges[:]
	newSingleResults = singleResults[:]
	matchCount = {}
	dataSeen = set()

	for singleResult in singleResults:
		for pixelatedSubRectange in pixelatedSubRectanges:
			if not isNeighbor(singleResult, pixelatedSubRectange):
				continue
			if pixelatedSubRectange in matchCount and matchCount[pixelatedSubRectange] > 1:
				break

			# use relative position to determine its neighbors
			for singleResultMatch in rectangleMatches[(singleResult.x, singleResult.y)]:
				for compareMatch in rectangleMatches[(pixelatedSubRectange.x, pixelatedSubRectange.y)]:

					xDistance = singleResult.x - pixelatedSubRectange.x
					yDistance = singleResult.y - pixelatedSubRectange.y
					xDistanceMatches = singleResultMatch.x - compareMatch.x
					yDistanceMatches = singleResultMatch.y - compareMatch.y

					if xDistance == xDistanceMatches and yDistance == yDistanceMatches:
						if repr((compareMatch.data, singleResultMatch.data)) not in dataSeen:

							dataSeen.add(repr((compareMatch.data, singleResultMatch.data)))

							if pixelatedSubRectange not in matchCount:
								matchCount[pixelatedSubRectange] = 1
							else:
								matchCount[pixelatedSubRectange] += 1

	for pixelatedSubRectange in matchCount:
		if matchCount[pixelatedSubRectange] == 1:
			newSingleResults.append(pixelatedSubRectange)
			newPixelatedSubRectanges.remove(pixelatedSubRectange)

	return newSingleResults, newPixelatedSubRectanges


def writeFirstMatchToImage(singleMatchRectangles, rectangleMatches, searchImage, unpixelatedOutputImage):

	for singleResult in singleMatchRectangles:
		singleMatch = rectangleMatches[(singleResult.x,singleResult.y)][0]

		for x in range(singleResult.width):
			for y in range(singleResult.height):

				color = searchImage.imageData[singleMatch.x+x][singleMatch.y+y]
				unpixelatedOutputImage.putpixel((singleResult.x+x,singleResult.y+y), color)


def writeRandomMatchesToImage(pixelatedSubRectanges, rectangleMatches, searchImage, unpixelatedOutputImage):

	for singleResult in pixelatedSubRectanges:

		singleMatch = choice(rectangleMatches[(singleResult.x,singleResult.y)])

		for x in range(singleResult.width):
			for y in range(singleResult.height):

				color = searchImage.imageData[singleMatch.x+x][singleMatch.y+y]
				unpixelatedOutputImage.putpixel((singleResult.x+x,singleResult.y+y), color)


def writeAverageMatchToImage(pixelatedSubRectanges, rectangleMatches, searchImage, unpixelatedOutputImage):

	for pixelatedSubRectange in pixelatedSubRectanges:

		coordinate = (pixelatedSubRectange.x, pixelatedSubRectange.y)
		matches = rectangleMatches[coordinate]

		img = Image.new('RGB', (pixelatedSubRectange.width, pixelatedSubRectange.height), color = 'white')

		for match in matches:

			dataCount = 0
			for x in range(pixelatedSubRectange.width):
				for y in range(pixelatedSubRectange.height):

					pixelData = match.data[dataCount]
					dataCount += 1
					currentPixel = img.getpixel((x,y))[0:3]

					r = int((pixelData[0]+currentPixel[0])/2)
					g = int((pixelData[1]+currentPixel[1])/2)
					b = int((pixelData[2]+currentPixel[2])/2)

					averagePixel = (r,g,b)

					img.putpixel((x,y), averagePixel)

		for x in range(pixelatedSubRectange.width):
			for y in range(pixelatedSubRectange.height):

				currentPixel = img.getpixel((x,y))[0:3]
				unpixelatedOutputImage.putpixel((pixelatedSubRectange.x+x,pixelatedSubRectange.y+y), currentPixel)

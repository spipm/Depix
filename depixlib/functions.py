from depixlib.Rectangle import *
from random import choice
from PIL import Image



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

	# checks if real rectange with same color. prefers horizontal rectangles
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


def removeMootColorRectangles(colorRectanges):

	pixelatedSubRectanges = []

	for colorRectange in colorRectanges:

			if colorRectange.color in [(0,0,0),(255,255,255)]:
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


def findRectangleMatches(rectangeSizeOccurences, pixelatedSubRectanges, searchImage):

	rectangleMatches = {}

	for rectangeSizeOccurence in rectangeSizeOccurences:

		rectangleSize = rectangeSizeOccurence
		rectangleWidth = rectangleSize[0]
		rectangleHeight = rectangleSize[1]
		pixelsInRectangle = rectangleWidth*rectangleHeight

		matchingRectangles = []
		for colorRectange in pixelatedSubRectanges:

			if (colorRectange.width, colorRectange.height) == rectangleSize:
				matchingRectangles.append(colorRectange)

		for x in range(searchImage.width - rectangleWidth):
			for y in range(searchImage.height - rectangleHeight):

				r = g = b = 0
				matchData = []

				for xx in range(rectangleWidth):

					for yy in range(rectangleHeight):
						newPixel = searchImage.imageData[x+xx][y+yy]
						rr,gg,bb = newPixel
						matchData.append(newPixel)

						r += rr
						g += gg
						b += bb

				averageColor = (int(r / pixelsInRectangle), int(g / pixelsInRectangle), int(b / pixelsInRectangle))

				for matchingRectangle in matchingRectangles:

					if (matchingRectangle.x,matchingRectangle.y) not in rectangleMatches:
						rectangleMatches[(matchingRectangle.x,matchingRectangle.y)] = []
					
					if matchingRectangle.color == averageColor:
						newRectangleMatch = RectangleMatch(x, y, matchData)
						rectangleMatches[(matchingRectangle.x,matchingRectangle.y)].append(newRectangleMatch)
	
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
		singleMatch = True
		
		for match in rectangleMatches[(colorRectange.x,colorRectange.y)]:

			if firstMatchData != match.data:
				singleMatch = False
				break

		if singleMatch:
			singleResults.append(colorRectange)
		else:
			newPixelatedSubRectanges.append(colorRectange)

	return singleResults, newPixelatedSubRectanges


def findGeometricMatchesForSingleResults(singleResults, pixelatedSubRectanges, rectangleMatches):

	tmpSingleResults = []
	newPixelatedSubRectanges = pixelatedSubRectanges[:]
	newSingleResults = singleResults[:]

	for singleResult in singleResults:

		totalMatches = 0

		singleResultMatchingRectangles = []
		dataSeen = []

		for singleResultMatch in rectangleMatches[(singleResult.x,singleResult.y)]:
			for pixelatedSubRectange in pixelatedSubRectanges:
				for compareMatch in rectangleMatches[(pixelatedSubRectange.x,pixelatedSubRectange.y)]:

					if (compareMatch.data,singleResultMatch.data) in dataSeen:
						continue

					xDistanceMatches = singleResultMatch.x - compareMatch.x
					xDistanceRectangles = singleResult.x - pixelatedSubRectange.x

					yDistanceMatches = singleResultMatch.y - compareMatch.y
					yDistanceRectangles = singleResult.y - pixelatedSubRectange.y

					if xDistanceMatches == xDistanceRectangles and yDistanceMatches == yDistanceRectangles:
						if xDistanceMatches == singleResult.width or xDistanceMatches == pixelatedSubRectange.width:
							if yDistanceMatches == singleResult.height or yDistanceMatches == pixelatedSubRectange.height:
								
								singleResultMatchingRectangles.append(pixelatedSubRectange)
								dataSeen.append((compareMatch.data,singleResultMatch.data))

								totalMatches += 1

		if totalMatches == 1:
			for singleResultMatchingRectangle in singleResultMatchingRectangles:
				tmpSingleResults.append(singleResultMatchingRectangle)

	for newSingleResult in tmpSingleResults:
		newSingleResults.append(newSingleResult)
		newPixelatedSubRectanges.remove(newSingleResult)

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

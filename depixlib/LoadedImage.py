from PIL import Image



class LoadedImage():

	def __init__(self, path):

		self.path = path
		self.loadedImage = False
		self.imageData = False

		self.loadImageData()


	def getCopyOfLoadedPILImage(self):
		return self.loadedImage.copy()


	def loadImage(self):

		self.loadedImage = Image.open(self.path)
		self.width = self.loadedImage.size[0]
		self.height = self.loadedImage.size[1]


	def loadImageData(self):
		''' Load data from image with getdata() because of the speed increase over consecutive calls to getpixel '''

		if self.loadedImage == False:
			self.loadImage()

		self.imageData = [[y for y in range(self.height)] for x in range(self.width)]

		rawData = self.loadedImage.getdata()
		rawDataCount = 0

		# because getdata returns the image as one big list
		for y in range(self.height):
			for x in range(self.width):

				self.imageData[x][y] = rawData[rawDataCount][0:3]
				rawDataCount += 1

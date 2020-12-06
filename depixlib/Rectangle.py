

class Rectangle():
	
	def __init__(self, startCoordinates, endCoordinates):
		
		self.startCoordinates = startCoordinates
		self.endCoordinates = endCoordinates

		self.x = self.startCoordinates[0]
		self.y = self.startCoordinates[1]

		self.width = self.endCoordinates[0] - self.x
		self.height = self.endCoordinates[1] - self.y


class ColorRectange(Rectangle):

	def __init__(self, color, startCoordinates, endCoordinates):

		super(ColorRectange, self).__init__(startCoordinates, endCoordinates)
		self.color = color
		

class RectangleMatch():

	def __init__(self, x, y, data):
		self.x = x
		self.y = y
		self.data = data
		

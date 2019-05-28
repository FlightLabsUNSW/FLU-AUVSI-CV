from Analysis import Analysis

class ODLC(object):
	def __init__(self, id, confidence, threshold, snapshot_time, image, latitude, longitude):
		self.id            = id
		self.confidence    = confidence
		self.threshold     = threshold
		self.snapshot_time = snapshot_time
		self.image         = image
		self.latitude      = latitude
		self.longitude     = longitude
		self.sent          = False

	@property
	def accept_obj(self):
		pass

	def set_threshold(self, threshold):
		self.threshold = threshold

class Person(ODLC):
	def __init__(self, id, confidence, threshold, snapshot_time, image, latitude, longitude):
		super().__init__(id, confidence, threshold, snapshot_time, image, latitude, longitude)

	def get_dict_to_send(self):
		dictionary = {
			"id":         self.id,
			"latitude":   self.latitude,
			"longitude":  self.longitude,
			"autonomous": False
		}

		return dictionary

class Shape(ODLC):
	def __init__(self, id, confidence, threshold, snapshot_time, image, latitude, longitude):
		super().__init__(id, confidence, threshold, snapshot_time, image, latitude, longitude)

		self.shape = None
		self.shape_colour = None
		self.character = None
		self.character_colour = None
		self.character_orientation = None
		self.is_off_axis = None
		self.autonomous = True

	# Method to run in analysis process
	def run_analysis(self, conn):
		analysis = Analysis(self.image)

		self.shape                 = analysis.get_shape()
		self.shape_colour          = analysis.get_shape_colour()
		self.character             = analysis.get_character()
		self.character_colour      = analysis.get_character_colour()
		self.character_orientation = analysis.get_character_orientation()

		conn.send(self)

	def get_dict_to_send(self):
		dictionary = {
			"id":         self.id,
			"shape":      self.shape,
			"shapeColor": self.shape_colour,
			"latitude":   self.latitude,
			"longitude":  self.longitude,
			"autonomous": self.autonomous
		}

		return dictionary
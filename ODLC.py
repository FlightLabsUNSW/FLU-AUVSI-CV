from Analysis import Analysis

import json
import zipfile
import cv2

class ODLC(object):
	SEND_THRESHOLD = 20

	def __init__(self, id, initial_confidence, initial_image, initial_latitude, initial_longitude, initial_image_distance, threshold, autonomous):
		self.id                 = id                     # Internal ID
		self.confidence         = initial_confidence     # Confidence that the object is correct
		self.threshold          = threshold              # Threshold for sending object to ground
		self.best_image         = initial_image          # Initial image of the object, updated to be the best one
		self.image_distance     = initial_image_distance # Distance of the best object to the drone's ground position
		self.latitude           = initial_latitude
		self.longitude          = initial_longitude
		self.num_objects        = 0                      # snapshot_time, image, shape, shape_colour, character, character_colour, character_orientation
		self.sent               = False                  # Whether or not the object has been sent to the ground station
		self.autonomous         = autonomous             # Whether or not the object was analaysed automatically

	def add_new_object(self, new_confidence, new_image, new_latitude, new_longitude, new_distance):
		
		# Get number of objects in ODLC
		num_objects = self.total_num_objects

		# Update ODLC confidence
		self.confidence = (self.confidence * num_objects + new_confidence) / (num_objects + 1)

		# Update latitude
		self.latitude = (self.latitude * num_objects + new_latitude) / (num_objects + 1)

		# Update longitude
		self.longitude = (self.longitude * num_objects + new_longitude) / (num_objects + 1)

		# Update best image
		if (new_distance < self.image_distance):
			self.best_image     = new_image
			self.image_distance = new_distance

	# Makes a zip folder containing a json string file and image of the object
	def send_object_to_ground(self):
		# Get dictionary with all the object data
		dictionary = self.get_dict_to_send()

		string = json.dumps(dictionary)

		ret, img_buff = cv2.imencode(".jpg", self.best_image)

		with zipfile.ZipFile("objects/" + str(self.id) + ".zip", "w") as myzip:
			myzip.writestr(str(self.id) + ".json", string)
			myzip.writestr(str(self.id) + ".png",  img_buff)

		self.sent = True

	def update_threshold(self):
		self.threshold += 0.01
		
class Shape(ODLC):
	def __init__(self, id, initial_confidence, initial_snapshot_time, initial_image, initial_latitude, initial_longitude, initial_image_distance, threshold):
		super().__init__(id, initial_confidence, initial_image, initial_latitude, initial_longitude, initial_image_distance, threshold, True)
		self.unanalysed_shapes      = [] # snapshot_time, imaage
		self.shapes                 = {}
		self.shape_colours          = {}
		self.characters             = {}
		self.character_colours      = {}
		self.character_orientation  = 0

		initial_object = {
			"snapshot_time": initial_snapshot_time,
			"image":         initial_image
		}

		self.unanalysed_shapes.append(initial_object)

	def add_new_shape(self, new_confidence, new_snapshot_time, new_image, new_latitude, new_longitude, new_distance):
		if (new_confidence < self.threshold):
			return False
		
		new_object = self.add_new_object(new_confidence, new_image, new_latitude, new_longitude, new_distance)

		# Create new unanalysed object
		new_object = {
			"snapshot_time": new_snapshot_time,
			"image":         new_image
		}

		# Add the new object to the unanalysed objects list
		self.unanalysed_shapes.append(new_object)

		# Update threshold
		#self.update_threshold()

		return True

	# Method to run in analysis process
	def run_analysis(self, conn):

		# Analyse each unanalysed object
		for unanalysed_object in self.unanalysed_shapes:

			# Start analysis on the new image object
			analysis = Analysis(unanalysed_object["image"])

			# Run each analysis
			shape                 = analysis.get_shape()
			shape_colour          = analysis.get_shape_colour()
			character             = analysis.get_character()
			character_colour      = analysis.get_character_colour()
			character_orientation = analysis.get_character_orientation()

			# Update occurances dictionaries
			self.add_shape(shape)
			self.add_shape_colour(shape_colour)
			self.add_character(character)
			self.add_character_colour(character_colour)
			self.add_character_orientation(character_orientation)

			# Increment the number of analysed objects
			self.num_objects += 1

		# Reset unanalysed objects list
		self.unanalysed_shapes = []

		# Check if object can be sent to ground
		if (self.completed):
			self.send_object_to_ground()

		# Send analysed ODLC class back to the manager process
		conn.send(self)

	def add_shape(self, shape):
		if (shape in self.shapes):
			self.shapes[shape] += 1
		else:
			self.shapes[shape] = 1

	def add_shape_colour(self, shape_colour):
		if (shape_colour in self.shape_colours):
			self.shape_colours[shape_colour] += 1
		else:
			self.shape_colours[shape_colour] = 1

	def add_character(self, character):
		if (character in self.characters):
			self.characters[character] += 1
		else:
			self.characters[character] = 1

	def add_character_colour(self, character_colour):
		if (character_colour in self.character_colours):
			self.character_colours[character_colour] += 1
		else:
			self.character_colours[character_colour] = 1

	def add_character_orientation(self, new_character_orientation):

		#if (self.character_orientation == None)

		# Get number of objects in ODLC not including the shape being analysed
		num_objects = self.num_objects + len(self.unanalysed_shapes) - 1

		self.character_orientation = (self.character_orientation * num_objects + new_character_orientation) / (num_objects + 1)

	@property
	def total_num_objects(self):
		return self.num_objects + len(self.unanalysed_shapes)

	@property
	def shape(self):

		# Get most common shape in shapes dictionary
		most_common_shape = None
		shape_occurances  = 0

		for shape, occurances in self.shapes.items():
			if (occurances > shape_occurances):
				most_common_shape = shape

		return most_common_shape

	@property
	def shape_colour(self):

		# Get most common shape colour in shape_colours dictionary
		most_common_shape_colour = None
		shape_colour_occurances  = 0

		for shape_colour, occurances in self.shape_colours.items():
			if (occurances > shape_colour_occurances):
				most_common_shape_colour = shape_colour

		return most_common_shape_colour

	@property
	def character(self):

		# Get most common shape colour in shape_colours dictionary
		most_common_character = None
		character_occurances  = 0

		for character, occurances in self.characters.items():
			if (occurances > character_occurances):
				most_common_character = character

		return most_common_character

	@property
	def character_colour(self):

		# Get most common shape colour in shape_colours dictionary
		most_common_character_colour = None
		character_colour_occurances  = 0

		for character_colour, occurances in self.character_colours.items():
			if (occurances > character_colour_occurances):
				most_common_character_colour = character_colour

		return most_common_character_colour

	@property
	def completed(self):
		# Check main confidence
		if (self.num_objects < self.SEND_THRESHOLD):
			return False

		return True

	def get_dict_to_send(self):
		dictionary = {
			"num objects seen":     self.num_objects,
			"shape":                self.shape,
			"shapeColor":           self.shape_colour,
			"character":            self.character,
			"characterColour":      self.character_colour,
			"characterOrientation": self.character_orientation,
			"latitude":             self.latitude,
			"longitude":            self.longitude,
			"autonomous":           self.autonomous
		}

		return dictionary

	def __str__(self):
		return str(self.id)

class Person(ODLC):
	def __init__(self, id, initial_confidence, initial_snapshot_time, initial_image, initial_latitude, initial_longitude, initial_image_distance, threshold):
		super().__init__(id, initial_confidence, initial_image, initial_latitude, initial_longitude, initial_image_distance, threshold, False)

	def add_new_person(self, new_confidence, new_snapshot_time, new_image, new_latitude, new_longitude, new_distance):
		if (new_confidence < self.threshold):
			return False

		# add the object
		new_object = self.add_new_object(new_confidence, new_image, new_latitude, new_longitude, new_distance)

		self.num_objects += 1

		# Update threshold
		self.update_threshold()

		return True

	def get_dict_to_send(self):
		dictionary = {
			"num objects seen": self.num_objects,
			"id":         self.id,
			"type":       "person",
			"latitude":   self.latitude,
			"longitude":  self.longitude,
			"autonomous": False
		}

		return dictionary

	@property
	def total_num_objects(self):
		return self.num_objects

	def __str__(self):
		return str(self.id)
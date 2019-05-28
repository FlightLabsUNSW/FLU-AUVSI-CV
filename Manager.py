from RealTimeProcess import real_time_process
from ODLC import Shape, Person
from IDGenerator import IDGenerator

import multiprocessing as mp
import cv2
import datetime
import json
import shutil
import math
import os
import zipfile
import numpy as np

SHAPE_THRESHOLD              = 0.5
LOCATION_DUPLICATE_THRESHOLD = 5 # Metres

class Manager:
	def __init__(self):
		self.id_generator = IDGenerator()

		# List of seen objects
		self.shapes = []
		self.people = []

		# Real time process with pipe
		parent_conn, child_conn = mp.Pipe()

		rtp = mp.Process(target=real_time_process, args=(child_conn,))
		rtp.start()

		# Analysis process pool and queue
		running_jobs = []
		jobs_queue   = []

		# Main loop
		while True:

			# Check if there is a new capture
			if (parent_conn.poll()):
				# Get image and objects list from real time process
				real_time_capture = parent_conn.recv()

				# Gets new shape and person objects
				new_shapes, new_people = self.process_capture(real_time_capture)

				self.people += new_people

				# Object analysis
				for shape_to_analyse in new_shapes:

					# Create new pipe and process for the unprocessed shape
					new_parent_conn, new_child_conn = mp.Pipe()

					process = mp.Process(target=shape_to_analyse.run_analysis, args=(new_child_conn,))

					job = {"process": process, "pipe": new_parent_conn}
					
					# If there is a free process start it, or else put it in the queue
					if (len(running_jobs) < 3):
						process.start()
						running_jobs.append(job)
					else:
						jobs_queue.append(job)

			# Poll analysis processes to see if they are done
			for job in running_jobs:

				# Check if shape is analysed
				if (job["pipe"].poll()):
					analysed_shape = job["pipe"].recv()

					print(analysed_shape.longitude)

					self.shapes.append(analysed_shape)

					print(str(self.shapes))
					
					#self.send_object_to_ground(analysed_shape)

					# If there is a job in the queue, start it
					if (len(jobs_queue) > 0):
						job = jobs_queue.pop(0)

						job["process"].start()
						running_jobs.append(job)

	# Makes a zip folder containing a json string file and image of the object
	def send_object_to_ground(self, object_to_send):
		# Get dictionary with all the object data
		dictionary = object_to_send.get_dict_to_send()

		string = json.dumps(dictionary)

		ret, img_buff = cv2.imencode(".jpg", object_to_send.image)

		with zipfile.ZipFile(str(object_to_send.id) + ".zip", "w") as myzip:
			myzip.writestr(str(object_to_send.id) + ".json", string)
			myzip.writestr(str(object_to_send.id) + ".png", img_buff)

	# Checks if a shape has already been detected
	def shape_exists(self, latitude, longitude):
		for shape in self.shapes:

			print(shape.longitude)
			distance = self.haversine(shape.latitude, shape.longitude, latitude, longitude)

			if (distance < LOCATION_DUPLICATE_THRESHOLD):
				return True

		return False
	
	# Checks if a person has already been detected
	def person_exists(self, latitude, longitude):
		for person in self.people:
			distance = self.haversine(person.latitude, person.longitude, latitude, longitude)

			if (distance < LOCATION_DUPLICATE_THRESHOLD):
				return True

		return False

	# Gets distance between 2 coordinates
	def haversine(self, lat1, long1, lat2, long2):
	    lat1  = float(lat1)
	    long1 = float(long1)
	    lat2  = float(lat2)
	    long2 = float(long2)

	    degree_to_rad = float(math.pi / 180.0)

	    d_lat  = (lat2  - lat1)  * degree_to_rad
	    d_long = (long2 - long1) * degree_to_rad

	    a = pow(math.sin(d_lat / 2), 2) + math.cos(lat1 * degree_to_rad) * math.cos(lat2 * degree_to_rad) * pow(math.sin(d_long / 2), 2)
	    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
	    
	    distance = (6367 * c) / 1000

	    return distance

	def process_capture(self, real_time_capture):
		snapshot_time       = datetime.datetime.now().time()
		image               = real_time_capture["image"]
		unprocessed_objects = real_time_capture["objects"]

		# Get image details
		height, width, channels = image.shape
		
		# Field of view
		fov = {
			"x": 60,
			"y": 60
		}

		# Get telemtry
		drone_latitude, drone_longitude = self.get_current_drone_coordinates()
		drone_angle    = self.get_current_drone_angle()
		drone_altitude = self.get_current_drone_altitude()
		drone_bearing  = self.get_current_drone_bearing()

		# Processed objects
		shapes = []
		people = []

		# Process each detected object
		for image_object in unprocessed_objects:
			confidence = image_object["confidence"]
			threshold  = SHAPE_THRESHOLD

			# Get the box around the object
			bounding_box = {
				"left":   image_object["left"],
				"top":    image_object["top"],
				"right":  image_object["right"],
				"bottom": image_object["bottom"]
			}

			# Get image of just the object
			crop_image = image[image_object["bottom"]:image_object["top"], image_object["left"]:image_object["right"]]

			# Get the centre pixel of the object
			x_pixel = int((image_object["left"] + image_object["right"]) / 2)
			y_pixel = int((image_object["bottom"] + image_object["top"]) / 2)

			object_pixel = {
				"x": x_pixel,
				"y": y_pixel
			}

			# Get the coordinates of the object
			latitude, longitude = self.get_object_coordinates(object_pixel, fov, width, height, drone_angle, drone_latitude, drone_longitude, drone_altitude, drone_bearing)

			# Not currently used!!!
			drone_data = {
				"x_angle":   drone_angle["x"],
				"y_angle":   drone_angle["y"],
				"latitude":  latitude,
				"longitude": longitude,
				"bearing":   drone_bearing,
				"altitude":  drone_altitude
			}

			# Check what class of object it is
			if (image_object["class"] == "shape"):

				# Check if shape exists
				if (not self.shape_exists(latitude, longitude)):
					
					# Make new shape and add it to the new shapes list
					id = self.id_generator.get_id()

					new_shape = Shape(id, confidence, threshold, snapshot_time, crop_image, latitude, longitude)
					shapes.append(new_shape)

			elif (image_object["class"] == "person"):

				# Check if person exists
				if (not self.person_exists(latitude, longitude)):
					
					# Make new person and add it to the new people list
					id = self.id_generator.get_id()

					new_person = Person(id, confidence, threshold, snapshot_time, crop_image, latitude, longitude)
					people.append(new_person)

		return shapes, people

	def get_current_drone_angle(self):
		x_angle = 0
		y_angle = 0

		return { "x": x_angle, "y": y_angle }

	def get_current_drone_altitude(self):
		altitude = 100
		
		return altitude

	def get_current_drone_bearing(self):
		bearing = 0
		
		return bearing

	def get_current_drone_coordinates(self):
		latitude  = 0
		longitude = 0
		
		return latitude, longitude

	def get_object_coordinates(self, object_pixel, fov, width, height, drone_angle, drone_latitude, drone_longitude, drone_altitude, drone_bearing):
		x_distance = self.get_1D_object_distance(fov["x"], object_pixel["x"], width,  drone_angle["x"], drone_altitude)
		y_distance = self.get_1D_object_distance(fov["y"], object_pixel["y"], height, drone_angle["y"], drone_altitude)

		distance = math.sqrt(x_distance ** 2 + y_distance ** 2)

		dot = y_distance
		det = x_distance

		object_bearing = math.atan2(det, dot)

		print("2D Object Ground Distance: " + str(distance))

		R       = 6378.1 # Radius of the Earth
		bearing = math.radians(drone_bearing) + object_bearing # Bearing converted to radians
		d       = distance / 1000 # Distance in km

		drone_latitude_radians  = math.radians(drone_latitude)  # Current lat point converted to radians
		drone_longitude_radians = math.radians(drone_longitude) # Current long point converted to radians

		latitude  = math.asin(math.sin(drone_latitude_radians) * math.cos(d / R) + math.cos(drone_latitude_radians) * math.sin(d / R) * math.cos(bearing))
		longitude = drone_longitude_radians + math.atan2(math.sin(bearing) * math.sin(d / R) * math.cos(drone_latitude_radians), math.cos(d / R) - math.sin(drone_latitude_radians) * math.sin(drone_latitude_radians))

		return math.degrees(latitude), math.degrees(longitude)

	def get_1D_object_distance(self, fov, object_pixel, length, drone_angle, drone_altitude):
		#print("1 Dimension Distance")

		centre_pixel = 0.5 * length
		#print("centre_pixel: " + str(centre_pixel))

		object_angle_ratio = (object_pixel - centre_pixel) / (0.5 * length)
		#print("object_angle_ratio: " + str(object_angle_ratio))

		object_angle = object_angle_ratio * (0.5 * fov)
		#print("object_angle_to_centre_pixel: " + str(object_angle) + " Degrees")

		object_angle_to_drone = drone_angle + object_angle
		#print("object_angle_to_drone: " + str(object_angle_to_drone) + " Degrees")

		object_distance_to_drone = math.tan(math.radians(object_angle_to_drone)) * drone_altitude
		#print("object_distance_to_drone: " + str(object_distance_to_drone) + "m\n")

		return object_distance_to_drone

if __name__ == "__main__":
	manager = Manager()
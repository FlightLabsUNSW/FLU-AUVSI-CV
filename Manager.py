from RealTimeProcess import real_time_process
from ODLC            import Shape, Person
from IDGenerator     import IDGenerator
from Telemetry       import Telemetry

import multiprocessing as mp
import cv2
import datetime
import json
import math
import os
import zipfile
import numpy as np

# Config

INITIAL_SHAPE_THRESHOLD      = 0.5 
LOCATION_DUPLICATE_THRESHOLD = 1   # Metres
NUM_ANALYSIS_PROCESSES       = 1

class Manager:
	def __init__(self, stop_manager):

		# ID generator to give unique ID to each object
		self.id_generator = IDGenerator()

		# List of seen objects
		self.shapes = []
		self.people = []

		# List of new unanalysed shapes with ODLC classes in the analysis pool
		self.shapes_queue = []

		# Analysis process pool and queue
		self.running_jobs            = []
		self.shapes_to_analyse_queue = []

		self.stop_manager = stop_manager

		# Telemetry process
		self.telemetry_pipe, telemetry_child_pipe = mp.Pipe()

		telemetry_object = Telemetry(self.telemetry_pipe, telemetry_child_pipe)

		self.telemetry = mp.Process(target=telemetry_object.listen)

		self.telemetry.start()

		# Real time process with pipe
		self.parent_conn, child_conn = mp.Pipe()

		self.rtp = mp.Process(target=real_time_process, args=(child_conn,))

		self.rtp.start()	

	def run(self):	

		# Main loop
		while True:		
			# Check termination request
			if (self.stop_manager.value):
				self.stop()
				break
			
			print("new capture")
			# Check if there is a new capture
			if (self.parent_conn.poll()):
				# Get image and objects list from real time process
				real_time_capture = self.parent_conn.recv()

				self.print_objects()

				# Gets new shape and person objects
				new_shapes, new_people = self.process_capture(real_time_capture)

				# Add new people to the seen people list
				self.people += new_people

				# Object analysis
				for shape_to_analyse in new_shapes:
					
					# If there is a free process start it, or else put it in the queue
					if (len(self.running_jobs) < NUM_ANALYSIS_PROCESSES):
						# Create new pipe and process for the unprocessed shape
						new_parent_conn, new_child_conn = mp.Pipe()

						process = mp.Process(target=shape_to_analyse.run_analysis, args=(new_child_conn,))

						job = {
							"process": process,
							"pipe":    new_parent_conn,
							"shape":   shape_to_analyse
						}

						process.start()
						self.running_jobs.append(job)
					else:
						self.shapes_to_analyse_queue.append(shape_to_analyse)

				self.print_objects()

			print("looping through analysis processes")
			unfinished_jobs = []

			# Poll analysis processes to see if they are done
			for job in self.running_jobs:

				# Check if shape is analysed
				if (job["pipe"].poll()):
					analysed_shape = job["pipe"].recv()

					self.shapes.append(analysed_shape)
					
					print("Object ID: " + str(analysed_shape.id) + " " + str(analysed_shape.get_dict_to_send()))

					# If there is a job in the queue, start it
					if (len(self.shapes_to_analyse_queue) > 0):
						print("loading new job")
						shape_to_analyse = self.shapes_to_analyse_queue.pop(0)

						new_parent_conn, new_child_conn = mp.Pipe()

						process = mp.Process(target=shape_to_analyse.run_analysis, args=(new_child_conn,))

						job = {
							"process": process,
							"pipe":    new_parent_conn,
							"shape":   shape_to_analyse
						}

						process.start()
						unfinished_jobs.append(job)
				else:
					unfinished_jobs.append(job)

			self.running_jobs = unfinished_jobs

	def stop(self):
		
		# End child processes and compile list of objects
		for job in self.running_jobs:
			while (not job["pipe"].poll()):
				pass

			analysed_shape = job["pipe"].recv()
			self.shapes.append(analysed_shape)

		# Send all objects to ground

		print("Sending all objects to ground")
		for shape in self.shapes + self.shapes_to_analyse_queue:
			print("Shape number: " + str(shape.id))
			if (not shape.sent):
				shape.send_object_to_ground()

		for person in self.people:
			print("Person number: " + str(person.id))
			if (not person.sent):
				person.send_object_to_ground()

	# Checks if a shape has already been detected
	def get_shape(self, latitude, longitude):
		for index, shape in enumerate(self.shapes):
			distance = self.haversine(shape.latitude, shape.longitude, latitude, longitude)

			if (distance < LOCATION_DUPLICATE_THRESHOLD):
				del self.shapes[index]
				return "analysed", shape

		for shape in self.shapes_to_analyse_queue:
			distance = self.haversine(shape.latitude, shape.longitude, latitude, longitude)

			if (distance < LOCATION_DUPLICATE_THRESHOLD):
				return "queued", shape

		for job in self.running_jobs:
			distance = self.haversine(job["shape"].latitude, job["shape"].longitude, latitude, longitude)

			if (distance < LOCATION_DUPLICATE_THRESHOLD):
				return "running", job["shape"] # self.shapes_queue.append(job["shape"])

		return None, None

	# Checks if a shape has already been detected
	def get_person(self, latitude, longitude):
		for person in self.people:
			distance = self.haversine(person.latitude, person.longitude, latitude, longitude)

			if (distance < LOCATION_DUPLICATE_THRESHOLD):
				return True, person

		return False, None

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
	    
	    distance = (6367 * c) * 1000

	    return distance

	def process_capture(self, real_time_capture):
		snapshot_time       = datetime.datetime.utcnow()
		image               = real_time_capture["image"]
		unprocessed_objects = real_time_capture["objects"]

		# Get image details
		height, width, channels = image.shape
		
		# Field of view
		fov = {
			"x": 120,
			"y": 120
		}

		# Get telemtry
		telemtry = self.get_telemetry(snapshot_time)

		drone_latitude  = telemtry["latitude"]
		drone_longitude = telemtry["longitude"]
		drone_angle    =  telemtry["angle"]
		drone_altitude =  telemtry["altitude"]
		drone_bearing  =  telemtry["bearing"]

		# Processed objects
		shapes = []
		people = []

		# Process each detected object
		for image_object in unprocessed_objects:

			confidence = image_object["confidence"]

			if (confidence < INITIAL_SHAPE_THRESHOLD):
				continue
			
			threshold  = INITIAL_SHAPE_THRESHOLD

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
			latitude, longitude, distance_to_drone = self.get_object_coordinates(object_pixel, fov, width, height, drone_angle, drone_latitude, drone_longitude, drone_altitude, drone_bearing)

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

				shape_detected, shape = self.get_shape(latitude, longitude)

				# Check if shape exists
				if (shape_detected == "analysed"):

					# Skip if shape has been sent
					if (shape.sent):
						self.shapes.append(shape)
						continue

					# Add new capture of shape
					success = shape.add_new_shape(confidence, snapshot_time, crop_image, latitude, longitude, distance_to_drone)

					# Check if the addition was successful. If not, add the shape back to the main shapes list
					if (success):
						shapes.append(shape)
					else:
						self.shapes.append(shape) 

				elif (shape_detected == "queued"):
					
					# Skip if shape has been sent
					if (shape.sent):
						continue

					# Add new capture of shape
					shape.add_new_shape(confidence, snapshot_time, crop_image, latitude, longitude, distance_to_drone)
				
				elif (shape_detected == "running"):

					# TODO
					image_object["latitude"]          = latitude
					image_object["longitude"]         = longitude
					image_object["image"]             = crop_image
					image_object["snapshot_time"]     = snapshot_time
					image_object["confidence"]        = confidence
					image_object["distance_to_drone"] = distance_to_drone

					#self.queue_shapes.append(image_object)

				else: # New shape

					# Make new shape and add it to the new shapes list
					id        = self.id_generator.get_id()
					new_shape = Shape(id, confidence, snapshot_time, crop_image, latitude, longitude, distance_to_drone, threshold)

					shapes.append(new_shape)

			elif (image_object["class"] == "person"):

				person_detected, person = self.get_person(latitude, longitude)

				# Check if person exists
				if (person_detected):
					
					person.add_new_person(confidence, snapshot_time, crop_image, latitude, longitude, distance_to_drone)

					print("Object ID: " + str(person.id) + " " + str(person.get_dict_to_send()))
				else:
					# Make new shape and add it to the new shapes list
					id         = self.id_generator.get_id()
					new_person = Person(id, confidence, snapshot_time, crop_image, latitude, longitude, distance_to_drone, threshold)

					print("Object ID: " + str(new_person.id) + " " + str(new_person.get_dict_to_send()))

					people.append(new_person)

		return shapes, people

	def get_telemetry(self, time):

		while True:
			if (self.telemetry_pipe.poll()):
				telemetry = self.telemetry_pipe.recv()
				#print(str(telemetry["time"]) + " | " + str(time))
				if telemetry["time"] >= time:
					break

		data = telemetry["data"]

		telemetry = {
			"angle": {
				"x": data.angular_position["x_angle"],
				"y": data.angular_position["y_angle"]
			},
			"altitude":  data.global_position["rel_alt"],
			"bearing":   data.global_position["compass_hdg"],
			"latitude":  data.global_position["latitude"],
			"longitude": data.global_position["longitude"]
		}

		return telemetry

	def get_object_coordinates(self, object_pixel, fov, width, height, drone_angle, drone_latitude, drone_longitude, drone_altitude, drone_bearing):
		x_distance = self.get_1D_object_distance(fov["x"], object_pixel["x"], width,  drone_angle["x"], drone_altitude)
		y_distance = self.get_1D_object_distance(fov["y"], object_pixel["y"], height, drone_angle["y"], drone_altitude)

		distance = math.sqrt(x_distance ** 2 + y_distance ** 2)

		dot = y_distance
		det = x_distance

		object_bearing = math.atan2(det, dot)

		#print("2D Object Ground Distance: " + str(distance))

		R       = 6378.1 # Radius of the Earth
		bearing = math.radians(drone_bearing) + object_bearing # Bearing converted to radians
		d       = distance / 1000 # Distance in km

		drone_latitude_radians  = math.radians(drone_latitude)  # Current lat point converted to radians
		drone_longitude_radians = math.radians(drone_longitude) # Current long point converted to radians

		latitude  = math.asin(math.sin(drone_latitude_radians) * math.cos(d / R) + math.cos(drone_latitude_radians) * math.sin(d / R) * math.cos(bearing))
		longitude = drone_longitude_radians + math.atan2(math.sin(bearing) * math.sin(d / R) * math.cos(drone_latitude_radians), math.cos(d / R) - math.sin(drone_latitude_radians) * math.sin(drone_latitude_radians))

		return math.degrees(latitude), math.degrees(longitude), distance

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

	def print_objects(self):
		shapes = []
		shapes_to_analyse_queue = []
		running_jobs = []

		for shape in self.shapes:
			shapes.append(shape.id)

		for shape in self.shapes_to_analyse_queue:
			shapes_to_analyse_queue.append(shape.id)

		for shape in self.running_jobs:
			running_jobs.append(shape["shape"].id)

		print("\nshapes list: " + str(shapes))
		print("queue list: " + str(shapes_to_analyse_queue))
		print("analysis processes: " + str(running_jobs) + "\n")
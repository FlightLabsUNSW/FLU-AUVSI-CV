from RealTimeProcess import real_time_process
from Analysis import Analysis
import multiprocessing as mp
import cv2
import pickle

def Manager:
	def __init__(self):
		# List of seen objects
		objects = []

		# Real time process with pipe
		parent_conn, child_conn = mp.Pipe()

		self.real_time_process = mp.Process(target=real_time_process, args=(child_conn,))
		self.real_time_process.start()

		# Analysis process pool and queue
		running_jobs = []
		jobs_queue   = []

		# Main loop
		while True:

			# Get image and objects list from real time process
			real_time_capture = parent_conn.recv()

			# Gets telemetry and processes objects
			image = Image(real_time_capture)

			objects_to_analyse = []

			# Get list of unseen objects
			for image_object in image.objects:
				if (not self.duplicate_exists(image_object)):
					objects_to_analyse.append(image_object)

			# Object analysis
			for object_to_analyse in objects_to_analyse:
				new_parent_conn, new_child_conn = mp.Pipe()

				process = mp.Process(target=self.analyse_object, args=(new_child_conn, object_to_analyse,))

				job = {"process": process, "pipe": new_parent_conn}
				
				if (len(running_jobs) < 3):
					process.start()
					running_jobs.append(job)
				else:
					jobs_queue.append()

			# Poll analysis processes to see if they are done
			for job in running_jobs:
				data = job["pipe"].recv()

				# Check if process sent anything
				if (len(data) > 0):
					analysed_object = pickle.loads(data)

					objects.append(analysed_object)
					
					self.send_object_to_ground()

					if (len(jobs_queue) > 0):
						job = jobs_queue.pop(0)

	# Sends an object to the ground station in a JSON string
	def send_object_to_ground(self, object_to_send):
		pass

	# Method to run in analysis process
	def analyse_object(self, conn, object_to_analyse):
		analysis = Analysis(object_to_analyse["image"])

		object_to_analyse["shape"]                 = analysis.get_shape()
		object_to_analyse["shape_colour"]          = analysis.get_shape_colour()
		object_to_analyse["character"]             = analysis.get_character()
		object_to_analyse["character_colour"]      = analysis.get_character_colour()
		object_to_analyse["character_orientation"] = analysis.get_character_orientation()

		conn.send(pickle.dumps(object_to_analyse))

	# Checks if an object has already been detected
	def duplicate_exists(self, new_object):
		for image_object in self.objects:
			distance = self.haversine(image_object.latitude, image_object.longitude, new_object.latitude, new_object.longitude)

			if (distance < 5):
				return True

		return False
	
	# Gets distance between 2 coordinates
	def haversine(self, lat1, long1, lat2, long2):
	    lat1  = float(lat1)
	    long1 = float(long1)
	    lat2  = float(lat2)
	    long2 = float(long2)

	    degree_to_rad = float(pi / 180.0)

	    d_lat  = (lat2  - lat1)  * degree_to_rad
	    d_long = (long2 - long1) * degree_to_rad

	    a = pow(sin(d_lat / 2), 2) + cos(lat1 * degree_to_rad) * cos(lat2 * degree_to_rad) * pow(sin(d_long / 2), 2)
	    c = 2 * atan2(sqrt(a), sqrt(1 - a))
	    
	    distance = (6367 * c) / 1000

	    return distance


def Image:
	def __init_(self, real_time_capture):
		image               = real_time_capture["image"]
		unprocessed_objects = real_time_capture["objects"]

		# Get image details
		height, width, channels = image.shape

		self.image  = image
		self.width  = width
		self.height = height
		self.fov    = 60

		# Get telemtry
		self.latitude, self.longitude          = self.get_current_drone_coordinates()
		self.drone_x_angle, self.drone_y_angle = self.get_current_drone_angle()

		self.drone_altitude = self.get_current_drone_altitude()
		self.drone_bearing  = self.get_current_drone_bearing()

		# Process objects
		self.objects = []

		for image_object in unprocessed_objects:
			new_image_object = {} 

			# Get image of just the object
			crop_image = image[image_object["bottom"]:image_object["top"], image_object["left"]:image_object["right"]]

			# Get the centre pixel of the object
			x_pixel = int((image_object["left"] + image_object["right"]) / 2)
			y_pixel = int((image_object["bottom"] + image_object["top"]) / 2) 

			# Get the coordinates of the object
			latitude, longitude = get_object_coordinates(x_pixel, y_pixel)
			
			# Add processed object to the objects list
			new_image_object["image"]     = crop_image
			new_image_object["latitude"]  = latitude
			new_image_object["longitude"] = longitude

			self.objects.append(new_image_object)

	def get_current_drone_angle(self):
		x_angle = 0
		y_angle = 0

		return x_angle, y_angle

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

	def get_object_coordinates(self, object_x_pixel, object_y_pixel):
		x_distance = self.get_1D_object_distance(self.fov.x, object_x_pixel, self.width,  self.drone_x_angle)
		y_distance = self.get_1D_object_distance(self.fov.y, object_y_pixel, self.height, self.drone_y_angle)

		distance = math.sqrt(x_distance ** 2 + y_distance ** 2)

		dot = y_distance
		det = x_distance

		object_bearing = math.atan2(det, dot)

		print("2D Object Ground Distance: " + str(distance))

		R       = 6378.1 # Radius of the Earth
		bearing = math.radians(self.drone_bearing) + object_bearing # Bearing converted to radians
		d       = distance / 1000 # Distance in km

		drone_latitude_radians  = math.radians(self.latitude)  # Current lat point converted to radians
		drone_longitude_radians = math.radians(self.longitude) # Current long point converted to radians

		latitude  = math.asin(math.sin(drone_latitude_radians) * math.cos(d / R) + math.cos(drone_latitude_radians) * math.sin(d / R) * math.cos(bearing))
		longitude = drone_longitude_radians + math.atan2(math.sin(bearing) * math.sin(d / R) * math.cos(drone_latitude_radians), math.cos(d / R) - math.sin(drone_latitude_radians) * math.sin(drone_latitude_radians))

		return math.degrees(latitude), math.degrees(longitude)

	def get_1D_object_distance(self, fov, object_pixel, length, drone_angle):
		print("1 Dimension Distance")

		centre_pixel = 0.5 * length
		print("centre_pixel: " + str(centre_pixel))

		object_angle_ratio = (object_pixel - centre_pixel) / (0.5 * length)
		#print("object_angle_ratio: " + str(object_angle_ratio))

		object_angle             = object_angle_ratio * (0.5 * fov)
		print("object_angle_to_centre_pixel: " + str(object_angle) + " Degrees")

		object_angle_to_drone    = drone_angle + object_angle
		print("object_angle_to_drone: " + str(object_angle_to_drone) + " Degrees")

		object_distance_to_drone = math.tan(math.radians(object_angle_to_drone)) * self.drone_altitude
		print("object_distance_to_drone: " + str(object_distance_to_drone) + "m\n")

		return object_distance_to_drone

if __name__ == "__main__":
	manager = Manager()
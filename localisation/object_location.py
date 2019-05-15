import math

class ImageObject:
	def __init__(self, x, y, classification):
		self.x = x
		self.y = y
		self.classification = classification 

class FOV:
	def __init__(self, x, y):
		self.x = x
		self.y = y

class Image:
	def __init__(self, image, width, height, latitude, longitude, drone_x_angle, drone_y_angle, drone_altitude, drone_bearing, fov, objects):
		self.image          = image
		self.width          = width
		self.height         = height
		self.latitude       = latitude
		self.longitude      = longitude
		self.drone_x_angle  = drone_x_angle
		self.drone_y_angle  = drone_y_angle
		self.drone_altitude = drone_altitude
		self.drone_bearing  = drone_bearing
		self.fov            = fov
		self.objects        = objects

	def get_object_coordinates(self, object_x_pixel, object_y_pixel):
		distance, object_bearing = self.get_object_distance(object_x_pixel, object_y_pixel)

		print("2D Object Ground Distance: " + str(distance))

		R       = 6378.1                # Radius of the Earth
		bearing = math.radians(self.drone_bearing) + object_bearing # Bearing converted to radians
		d       = distance / 1000       # Distance in km

		drone_latitude_radians  = math.radians(self.latitude)  # Current lat point converted to radians
		drone_longitude_radians = math.radians(self.longitude) # Current long point converted to radians

		latitude  = math.asin(math.sin(drone_latitude_radians) * math.cos(d / R) + math.cos(drone_latitude_radians) * math.sin(d / R) * math.cos(bearing))
		longitude = drone_longitude_radians + math.atan2(math.sin(bearing) * math.sin(d / R) * math.cos(drone_latitude_radians), math.cos(d / R) - math.sin(drone_latitude_radians) * math.sin(drone_latitude_radians))

		return math.degrees(latitude), math.degrees(longitude)

	def get_object_bearing(self, x, y):
		dot = x * 0 + y * 1
		det = x * 1 - y * 0

		return math.atan2(det, dot)

	def get_object_distance(self, object_x_pixel, object_y_pixel):
		x_distance = self.get_1D_object_distance(self.fov.x, object_x_pixel, self.width,  self.drone_x_angle)
		y_distance = self.get_1D_object_distance(self.fov.y, object_y_pixel, self.height, self.drone_y_angle)

		return math.sqrt(x_distance ** 2 + y_distance ** 2), self.get_object_bearing(x_distance, y_distance)

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


# Camera settings
IMAGE_WIDTH    = 100 # Pixels
IMAGE_HEIGHT   = 100 # Pixels
DRONE_FOV      = FOV(90, 90) # Degrees

# Drone position settings
DRONE_X_ANGLE  = 45 # Degrees
DRONE_Y_ANGLE  = 45 # Degrees
DRONE_ALTITUDE = 100 # Metres

LATITUDE       = -33.9189817 # Degrees
LONGITUDE      = 151.2316007 # Degrees
DRONE_BEARING  = 270 # Degrees

# Object position in image
OBJECT_X_PIXEL = 50
OBJECT_Y_PIXEL = 50

image = Image(None, IMAGE_WIDTH, IMAGE_HEIGHT, LATITUDE, LONGITUDE, DRONE_X_ANGLE, DRONE_Y_ANGLE, DRONE_ALTITUDE, DRONE_BEARING, DRONE_FOV, None)

test = image.get_object_coordinates(OBJECT_X_PIXEL, OBJECT_Y_PIXEL)

print("Drone Coordinates: " + str(LATITUDE) + ", " + str(LONGITUDE))
print("Object Coordinates: " + str(test))
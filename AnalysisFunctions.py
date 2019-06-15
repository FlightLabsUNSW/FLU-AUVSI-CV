import cv2
import numpy as np
import webcolors

from PIL import Image

def get_most_common_color(img):
	img = cv2.GaussianBlur(img, (61, 61), 10000)

	im_pil = Image.fromarray(img)

	def most_frequent_colour(image):

	    w, h = image.size
	    pixels = image.getcolors(w * h)

	    most_frequent_pixel = pixels[0]

	    for count, colour in pixels:
	        if count > most_frequent_pixel[0]:
	            most_frequent_pixel = (count, colour)

	    most_frequent_pixel = most_frequent_pixel[1]

	    return (most_frequent_pixel[2], most_frequent_pixel[1], most_frequent_pixel[0])

	requested_colour = most_frequent_colour(im_pil)

	colors = [
	    "red",
	    "blue",
	    "black",
	    "white",
	    "green",
	    "yellow",
	    "brown",
	    "orange"
	]

	def valid_color(name):
	    for color in colors:
	        if color in name:
	            return True, color

	    return False, None

	def closest_colour(requested_colour):
	    min_colours = {}
	    for key, name in webcolors.css3_hex_to_names.items():

	        is_valid, color = valid_color(name)

	        if not is_valid:
	            continue
	        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
	        rd = (r_c - requested_colour[0]) ** 2
	        gd = (g_c - requested_colour[1]) ** 2
	        bd = (b_c - requested_colour[2]) ** 2
	        min_colours[(rd + gd + bd)] = color

	    return min_colours[min(min_colours.keys())]

	closest_name = closest_colour(requested_colour)
	
	return closest_name.upper()

img = cv2.imread("test5.jpg")

print(get_most_common_color(img))
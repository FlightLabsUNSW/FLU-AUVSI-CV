import cv2
import numpy as np
import webcolors

from PIL import Image

img = cv2.imread("test2.png")

img = cv2.GaussianBlur(img, (61, 61), 10000)

#img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
im_pil = Image.fromarray(img)

def most_frequent_colour(image):

    w, h = image.size
    pixels = image.getcolors(w * h)

    most_frequent_pixel = pixels[0]

    for count, colour in pixels:
        if count > most_frequent_pixel[0]:
            most_frequent_pixel = (count, colour)

    #compare("Most Common", image, most_frequent_pixel[1])

    most_frequent_pixel = most_frequent_pixel[1]

    return (most_frequent_pixel[2], most_frequent_pixel[1], most_frequent_pixel[0])

requested_colour = most_frequent_colour(im_pil)

print(requested_colour)

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

def get_colour_name(requested_colour):
    try:
        closest_name = actual_name = webcolors.rgb_to_name(requested_colour)
    except ValueError:
        closest_name = closest_colour(requested_colour)
        actual_name = None
    return actual_name, closest_name


actual_name, closest_name = get_colour_name(requested_colour)
print(closest_name)

"""
img = cv2.imread('test2.png',cv2.IMREAD_UNCHANGED)

#img = cv2.GaussianBlur(img, (51,51), 100000)

data = np.reshape(img, (-1,3))
data = np.float32(data)

criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
flags = cv2.KMEANS_RANDOM_CENTERS
compactness, labels, centers = cv2.kmeans(data, 1, None, criteria, 10, flags)

print(type(centers[0].astype(np.int32)))

color = centers[0].astype(np.int32)

print(color)

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

def get_colour_name(requested_colour):
    try:
        closest_name = actual_name = webcolors.rgb_to_name(requested_colour)
    except ValueError:
        closest_name = closest_colour(requested_colour)
        actual_name = None
    return actual_name, closest_name

requested_colour = (color[2], color[1], color[0])
actual_name, closest_name = get_colour_name(requested_colour)

print(closest_name)

#for key, name in webcolors.css3_hex_to_names.items():
#    print(name)

"""

"""
import numpy as np
from matplotlib import pyplot as plt
import cv2

#data = np.random.normal(128, 1, (100, 100)).astype('float32')
data = np.random.randint(0, 256, (100, 100), 'uint8')
BINS = 20

np_hist, _ = np.histogram(data, bins=BINS)

dmin, dmax, _, _ = cv2.minMaxLoc(data)
if np.issubdtype(data.dtype, 'float'): dmax += np.finfo(data.dtype).eps
else: dmax += 1

cv_hist = cv2.calcHist([data], [0], None, [BINS], [dmin, dmax]).flatten()

plt.plot(np_hist, '-', label='numpy')
plt.plot(cv_hist, '-', label='opencv')
plt.gcf().set_size_inches(15, 7)
plt.legend()
plt.show()
"""
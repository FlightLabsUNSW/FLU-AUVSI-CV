"""
import multiprocessing as mp
from   multiprocessing import Process, Lock
from   multiprocessing.sharedctypes import Value

class Test:
	def __init__(self, blah):
		self.blah = blah

test = Test(1)

value = Value("i")

process = Process(target=test.test, args=(new_child_conn,))

process.start()

test = Test(2)

while True:
	print(new_parent_conn.recv())


import cv2

image = cv2.imread("test2.png")

#cv2.calcHist(image)
image.bincount
"""
import math

def haversine(lat1, long1, lat2, long2):
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

print(haversine(0.0003688967176222222, -0.00027670994685362023, 0.00036889671762222186, -0.0002767099468536204))
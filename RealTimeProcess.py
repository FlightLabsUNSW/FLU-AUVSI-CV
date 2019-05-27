import cv2
import pickle

def real_time_process(conn):
	while True:
		image = cv2.imread("test2.png")

		capture = {
			"image": image,
			"objects": [
				{ "class": "shape", "confidence": 0.9, "left": 0, "top": 100, "right": 100, "bottom": 0 },
				{ "class": "person", "confidence": 0.9, "left": 100, "top": 200, "right": 200, "bottom": 100 }
			]
		}

		conn.send(capture)
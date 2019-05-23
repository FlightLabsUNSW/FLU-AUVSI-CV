import cv2
import pickle

def real_time_process(conn):
	while True:
		conn.send()
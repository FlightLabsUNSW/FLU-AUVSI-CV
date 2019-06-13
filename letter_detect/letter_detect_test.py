import numpy as np
import cv2
from matplotlib import pyplot as plt
import sys
import time

# =====
# Detector, Descriptor and Matcher
# =====
#detector = cv2.ORB_create()
detector = cv2.BRISK(thresh=10, octaves=1)
descriptor = cv2.BRISK_create()
matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck = True)

MIN_MATCH_COUNT = 3

# =====
# Reading and Preparing the images
# =====
# Reference Object to be Searched
img1 = cv2.imread('Y.png')
# Image to be Searched
img2 = cv2.imread('test2_roi.png')

# Find the Edges with Canny Edges
canny1 = cv2.Canny(img1, 100, 500)
canny2 = cv2.Canny(img2, 100, 500)
cv2.imshow("Frame", canny1)
print(canny1.dtype)
time.sleep(5)

# Convert the Images to Grayscale
test1_image = cv2.cvtColor(canny1, cv2.COLOR_BGR2RGB)
test1_image = cv2.cvtColor(test1_image, cv2.COLOR_RGB2GRAY)
test2_image = cv2.cvtColor(canny2, cv2.COLOR_BGR2RGB)
test2_image = cv2.cvtColor(test2_image, cv2.COLOR_RGB2GRAY)


#kp1 = detector.detect(test1_image, None)
#kp2 = detector.detect(test2_image, None)

#print(kp1)
#kp1, des1 = descriptor.compute(test1_image, kp1)
#kp2, des2 = descriptor.compute(test2_image, kp2)
#print(kp1, des1)
kp2,des2 = descriptor.detectAndCompute(test2_image, None)
print(kp2,des2)

matches = matcher.match(des1, des2)
if len(matches) < MIN_MATCH_COUNT:
    print("Not enough matches found!")
    sys.exit()

# The matches with shorter distance are the ones we want.
matches = sorted(matches, key = lambda x : x.distance)

result = cv2.drawMatches(test1_image, kp1, test2_image, kp1, matches[:10], test2_image, flags = 2)
plt.imshow(result)
plt.show()

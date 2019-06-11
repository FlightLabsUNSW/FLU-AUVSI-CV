#!/usr/bin/python3
# 2017.11.26 23:27:12 CST

## Find object by orb features matching

import numpy as np
import cv2
imgname = "Y.png"          # query image (small object)
imgname2 = "test2_roi.png" # train image (large scene)

MIN_MATCH_COUNT = 4

## Create ORB object and BF object(using HAMMING)
orb = cv2.ORB_create()
img1 = cv2.imread(imgname)
img2 = cv2.imread(imgname2)

# Find the Edges with Canny Edges
canny1 = cv2.Canny(img1, 100, 500)
canny2 = cv2.Canny(img2, 100, 500)

# Convert the Images to Grayscale
test1_image = cv2.cvtColor(canny1, cv2.COLOR_BGR2RGB)
test1_gray = cv2.cvtColor(test1_image, cv2.COLOR_RGB2GRAY)
test2_image = cv2.cvtColor(canny2, cv2.COLOR_BGR2RGB)
test2_gray = cv2.cvtColor(test2_image, cv2.COLOR_RGB2GRAY)

cv2.imshow("Test 1", test1_gray)
cv2.imshow("Test 2", test2_gray)

## Find the keypoints and descriptors with ORB
kpts1, descs1 = orb.detectAndCompute(test1_gray, None)
kpts2, descs2 = orb.detectAndCompute(test2_gray, None)

## match descriptors and sort them in the order of their distance
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
matches = bf.match(descs1, descs2)
dmatches = sorted(matches, key = lambda x:x.distance)

if len(dmatches) == MIN_MATCH_COUNT:

    ## extract the matched keypoints
    src_pts  = np.float32([kpts1[m.queryIdx].pt for m in dmatches]).reshape(-1,1,2)
    dst_pts  = np.float32([kpts2[m.trainIdx].pt for m in dmatches]).reshape(-1,1,2)

    ## find homography matrix and do perspective transform
    M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,50.0)
    print(src_pts, dst_pts, M, mask)
    h,w = img1.shape[:2]
    pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
    dst = cv2.perspectiveTransform(pts,M)

    ## draw found regions
    img2 = cv2.polylines(img2, [np.int32(dst)], True, (0,0,255), 1, cv2.LINE_AA)
    cv2.imshow("found", img2)

    ## draw match lines
    res = cv2.drawMatches(img1, kpts1, img2, kpts2, dmatches[:20],None,flags=2)

    cv2.imshow("orb_match", res);

cv2.waitKey();cv2.destroyAllWindows()

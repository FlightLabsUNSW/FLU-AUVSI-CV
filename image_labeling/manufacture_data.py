import os
import cv2 as cv
#from imutils import rotate_bound
import random
import numpy as np
import queue

DEBUG = False

# Initial values
empty_imgs_dir = 'empty_imgs'
flu_odlcs_dir = 'flu_odlcs'
cwd = os.getcwd()
empty_imgs = os.listdir(os.path.join(cwd, empty_imgs_dir))
flu_odlcs = os.listdir(os.path.join(cwd, flu_odlcs_dir))

# Max number
num_obj_in_img = 10

# Modified imutils rotate_bound function
# Simply changing how the warpaffine function is called
def rotate_bound(image, angle):
    # grab the dimensions of the image and then determine the
    # center
    (h, w) = image.shape[:2]
    (cX, cY) = (w / 2, h / 2)

    # grab the rotation matrix (applying the negative of the
    # angle to rotate clockwise), then grab the sine and cosine
    # (i.e., the rotation components of the matrix)
    M = cv.getRotationMatrix2D((cX, cY), -angle, 1.0)
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])

    # compute the new bounding dimensions of the image
    nW = int((h * sin) + (w * cos))
    nH = int((h * cos) + (w * sin))

    # adjust the rotation matrix to take into account translation
    M[0, 2] += (nW / 2) - cX
    M[1, 2] += (nH / 2) - cY

    # perform the actual rotation and return the image
    return cv.warpAffine(
            image, 
            M, 
            (nW, nH), 
            cv.INTER_LINEAR, 
            borderMode=cv.BORDER_CONSTANT, 
            borderValue=(255,255,255)
            )


# Initialise the info about each odlc
li = []
for flu_shape in flu_odlcs:
    qu = queue.Queue()
    def onMouse(event, x, y, flags, param):
        if event == cv.EVENT_LBUTTONDOWN:
           # draw circle here (etc...)
           print('x = %d, y = %d'%(x, y))
           qu.put((x,y), False)
    cv.namedWindow(flu_shape)
    cv.setMouseCallback(flu_shape, onMouse)

    meta_list = flu_shape.split('_')
    meta = {}
    meta['alpha_num'] = meta_list[0]
    meta['alpha_colour'] = meta_list[1]
    meta['shape'] = meta_list[2]
    meta['shape_colour'], meta['image_type'] = meta_list[-1].split('.')
    meta['file_name'] = flu_shape

    odlc_path = os.path.join(cwd, flu_odlcs_dir, meta['file_name'])
    odlc_arr = cv.imread(odlc_path)
    cv.imshow(f"{meta['file_name']}", odlc_arr)
    cv.waitKey(0)
    while not qu.empty():
        meta['char_top_left'] = qu.get(False)
        meta['char_bottom_right'] = qu.get(False)
    cv.destroyAllWindows()
    print(meta)
    li.append(meta)


flu_odlcs = li

for img in empty_imgs:
    img_path = os.path.join(cwd, empty_imgs_dir, img)
    img_arr = cv.imread(img_path)

    added_odlcs = random.sample(flu_odlcs, random.randint(0,num_obj_in_img))
    
    for odlc in added_odlcs:
        odlc_path = os.path.join(cwd, flu_odlcs_dir, odlc['file_name'])

        odlc_arr = cv.imread(odlc_path)
        if DEBUG: print(odlc_arr, odlc_arr.shape)
        scale = 8
        odlc_arr = cv.resize(odlc_arr, tuple([int(odlc_arr.shape[0]/scale), int(odlc_arr.shape[1]/scale)]))
        odlc_arr = rotate_bound(odlc_arr, random.randrange(-180,180))

        if DEBUG:
            cv.imshow(odlc['file_name'], odlc_arr)
            cv.waitKey(0)
            cv.destroyAllWindows()

        top_left = random.randint(0, img_arr.shape[0]-odlc_arr.shape[0]), random.randint(0, img_arr.shape[1]-odlc_arr.shape[1])
        
        if DEBUG:
            print((img_arr.shape[0]-odlc_arr.shape[0], img_arr.shape[1]-odlc_arr.shape[1]))
            print(img_arr.shape)
            print(odlc_arr.shape)
            print(top_left)

        for col in range(odlc_arr.shape[1]): 
            for row in range(odlc_arr.shape[0]):
                if np.array(odlc_arr[row,col]).sum() < np.array((240,240,240)).sum():
                    ins = odlc_arr[row, col]

                    insert_point = top_left+np.array((row, col))
                    try:
                        img_arr[insert_point[0], insert_point[1]] = ins
                    except Exception as err:
                        print('Out of bounds error start:')
                        print((row, col))
                        print(odlc_arr[row].shape)
                        print(insert_point[0], insert_point[1])
                        print(img_arr.shape)
                        print(insert_point[0], img_arr[insert_point[0]].shape)
                        raise err
    cv.imshow('image '+img, img_arr)
    cv.waitKey(0)
    cv.destroyAllWindows()

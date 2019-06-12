import os
import cv2 as cv
#from imutils import rotate_bound
import random
import numpy as np
import queue
from enum import Enum
import json

DEBUG = False

class Formatter(Enum):
    yolo_dataset = 0
    icdar_dataset = 1

# Initial values
data_format = Formatter.yolo_dataset
empty_imgs_dir = 'empty_imgs'
flu_odlcs_dir = 'flu_odlcs'
out_dir = 'genobjdet_labeled_dataset'
cwd = os.getcwd()
empty_imgs = os.listdir(os.path.join(cwd, empty_imgs_dir))
flu_odlcs = sorted(os.listdir(os.path.join(cwd, flu_odlcs_dir)))

# Max number
num_obj_in_img = 3
odlc_scale = 2

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
            ), M, (nW, nH)




# Initialise the info about each odlc
li = []
for flu_odlc_file in flu_odlcs:

    if flu_odlc_file.endswith('.txt'):
        with open(os.path.join(cwd, flu_odlcs_dir, flu_odlc_file), 'r') as meta_file:
            meta = json.load(meta_file)

        meta['file_name'] = flu_odlc_file.split('.')[0] + '.png'

        meta['yolo_text'] = {}
        allx, ally = [], []
        x_center, y_center = 0, 0
        for key, val in meta['icdar_text'].items():
            x_center += val[0]
            y_center += val[1]
            allx.append(val[0])
            ally.append(val[1])
        x_center /= 4
        y_center /= 4
        allx.sort()
        ally.sort()
        meta['yolo_text']['x_center'] = x_center
        meta['yolo_text']['y_center'] = y_center
        meta['yolo_text']['width'] = allx[-1] - allx[0]
        meta['yolo_text']['height'] = ally[-1] - ally[0]
    
        li.append(meta)

flu_odlcs = li
num_images = 0
img_odlc_num = 0
for img in empty_imgs:
    num_images += 1
    ins_string = ''
    if DEBUG:
        print(num_images)
        print('going through', img)
    img_path = os.path.join(cwd, empty_imgs_dir, img)
    img_arr = cv.imread(img_path)

    added_odlcs = random.sample(flu_odlcs, random.randint(0,num_obj_in_img))
    if DEBUG: print('Adding odls:', added_odlcs, 'to', img)
    for odlc in added_odlcs:
        odlc_path = os.path.join(cwd, flu_odlcs_dir, odlc['file_name'])
        if data_format == Formatter.icdar_dataset:
            curr_odlc_shape_loc = odlc['icdar_shape'].copy()
        elif data_format == Formatter.yolo_dataset:
            curr_odlc_shape_loc = {'centre': (
                odlc['yolo_spot']['x_center'],
                odlc['yolo_spot']['y_center']
                )}

        odlc_arr = cv.imread(odlc_path, cv.IMREAD_UNCHANGED)
        if DEBUG: print(odlc_arr, odlc_arr.shape)
        scale = odlc_scale
        if DEBUG: print('resizing odlc')
        odlc_arr = cv.resize(odlc_arr, tuple([int(odlc_arr.shape[0]/scale), int(odlc_arr.shape[1]/scale)]))
        for key,val in curr_odlc_shape_loc.items():
            curr_odlc_shape_loc[key] = int(val[0]/scale), int(val[1]/scale)

        if DEBUG: print('rotating odlc')
        odlc_arr, rot_mat, res_size = rotate_bound(odlc_arr, random.randrange(-180,180))


        for key,val in curr_odlc_shape_loc.items():
            curr_odlc_shape_loc[key] = (
                    int(rot_mat[0,0]*val[0] + rot_mat[0,1]*val[1] + rot_mat[0,2]),
                    int(rot_mat[1,0]*val[0] + rot_mat[1,1]*val[1] + rot_mat[1,2])
                    )

        top_left = random.randint(0, img_arr.shape[0]-odlc_arr.shape[0]), random.randint(0, img_arr.shape[1]-odlc_arr.shape[1])

        for key,val in curr_odlc_shape_loc.items(): 
            curr_odlc_shape_loc[key] = int(val[0] + top_left[0]), int(val[1] + top_left[1])
        
        if DEBUG:
            print((img_arr.shape[0]-odlc_arr.shape[0], img_arr.shape[1]-odlc_arr.shape[1]))
            print(img_arr.shape)
            print(odlc_arr.shape)
            print(top_left)

        if DEBUG: print('putting odlc into image')
        for col in range(odlc_arr.shape[1]): 
            for row in range(odlc_arr.shape[0]):
                if odlc_arr[row,col,-1] > 10:
                    ins = odlc_arr[row, col, :3]

                    insert_point = top_left+np.array((row, col))
                    alpha, beta, gamma = [0.6,0.3,0.1]
                    try:
                        img_arr[insert_point[0], insert_point[1]] = img_arr[insert_point[0], insert_point[1]] * beta + ins * alpha + gamma
                    except Exception as err:
                        print('Out of bounds error start:')
                        print((row, col))
                        print(odlc_arr[row].shape)
                        print(insert_point[:2][::-1])
                        print(insert_point[0], insert_point[1])
                        print(img_arr.shape)
                        print(insert_point[0], img_arr[insert_point[0]].shape)
                        print(ins)
                        raise err

        if DEBUG:
            cv.imshow('image', img_arr)
            cv.waitKey(0)
            cv.destroyAllWindows()

        if data_format == Formatter.yolo_dataset:
            ins_string += str(20) + ' '
            for key,val in curr_odlc_shape_loc.items():
                ins_string += str(val[0]/img_arr.shape[0]) + ' '
                ins_string += str(val[1]/img_arr.shape[1]) + ' '
            ins_string += str(odlc['yolo_spot']['width']/img_arr.shape[0]) + ' '
            ins_string += str(odlc['yolo_spot']['height']/img_arr.shape[1]) + ' '
            ins_string += '\n'
            if DEBUG: print(str(img_odlc_num)+'.txt', ins_string, end='')
            
        elif data_format == Formatter.icdar_dataset:
            for key,val in curr_odlc_shape_loc.items():
                ins_string += str(val[0]) + ',' + str(val[1]) + ','
            ins_string += 'shape' + '\n'
            if DEBUG: print(str(img_odlc_num)+'.txt', ins_string, end='')


    if DEBUG:
        cv.imshow('image', img_arr)
        cv.waitKey(0)
        cv.destroyAllWindows()

    if DEBUG: print('inserting into', str(img_odlc_num) +'.txt')
    with open(os.path.join(cwd, out_dir, str(img_odlc_num) + '.txt'), 'w') as img_file:
        img_file.write(ins_string)

    cv.imwrite(os.path.join(cwd, out_dir, str(img_odlc_num) + '.jpg'), img_arr)

    if data_format == Formatter.yolo_dataset:
        with open(os.path.join(cwd, 'train.txt'), 'a') as train_file:
            train_file.write(os.path.join(cwd, out_dir, str(img_odlc_num) + '.jpg') + '\n')


    if DEBUG: print('finishing inserting into', str(img_odlc_num) + '.txt')
    with open(os.path.join(cwd, out_dir, str(img_odlc_num) + '.txt'), 'a') as img_file:
        img_file.write('')

    img_odlc_num += 1


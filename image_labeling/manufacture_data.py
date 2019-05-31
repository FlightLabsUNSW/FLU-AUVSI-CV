import os
import cv2 as cv
#from imutils import rotate_bound
import random
import numpy as np
import queue
from enum import Enum

DEBUG = False

class Formatter(Enum):
    yolo_dataset = 0
    icdar_dataset = 1

# Initial values
data_format = Formatter.yolo_dataset
empty_imgs_dir = 'empty_imgs'
flu_odlcs_dir = 'flu_odlcs'
out_dir = 'labeled_dataset'
cwd = os.getcwd()
empty_imgs = os.listdir(os.path.join(cwd, empty_imgs_dir))
flu_odlcs = os.listdir(os.path.join(cwd, flu_odlcs_dir))

# Max number
num_obj_in_img = 10
odlc_scale = 6

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
classes = []
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
    if meta['alpha_num'] in classes:
        meta['class_id'] = classes.index(meta['alpha_num'])
    else:
        classes.append(meta['alpha_num'])
        meta['class_id'] = len(classes)-1
    meta['alpha_colour'] = meta_list[1]
    meta['shape'] = meta_list[2]
    meta['shape_colour'], meta['image_type'] = meta_list[-1].split('.')
    meta['file_name'] = flu_shape

    odlc_path = os.path.join(cwd, flu_odlcs_dir, meta['file_name'])
    odlc_arr = cv.imread(odlc_path)
    cv.imshow(meta['file_name'], odlc_arr)
    cv.waitKey(0)
    meta['icdar_text'] = {}
    meta['yolo_text'] = {}
    while not qu.empty():
        meta['icdar_text']['xy1'] = qu.get(False)
        if not qu.empty():
            meta['icdar_text']['xy2'] = qu.get(False)
        if not qu.empty():
            meta['icdar_text']['xy3'] = qu.get(False)
        if not qu.empty():
            meta['icdar_text']['xy4'] = qu.get(False)
    cv.destroyAllWindows()

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
    

    
    print(meta)
    li.append(meta)

if data_format == Formatter.yolo_dataset:
    with open(os.path.join(cwd, 'flu_odlcs.names'), 'w') as class_file:
        for alpha in classes:
            class_file.write(alpha + '\n')


flu_odlcs = li
num_images = 0
img_odlc_num = 0
for img in empty_imgs:
    num_images += 1
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
            curr_odlc_text_loc = odlc['icdar_text'].copy()
        elif data_format == Formatter.yolo_dataset:
            curr_odlc_text_loc = {'centre': (
                odlc['yolo_text']['x_center'],
                odlc['yolo_text']['y_center']
                )}

        odlc_arr = cv.imread(odlc_path)
        if DEBUG: print(odlc_arr, odlc_arr.shape)
        scale = odlc_scale
        if DEBUG: print('resizing odlc')
        odlc_arr = cv.resize(odlc_arr, tuple([int(odlc_arr.shape[0]/scale), int(odlc_arr.shape[1]/scale)]))
        for key,val in curr_odlc_text_loc.items():
            curr_odlc_text_loc[key] = int(val[0]/scale), int(val[1]/scale)

        if DEBUG: print('rotating odlc')
        odlc_arr, rot_mat, res_size = rotate_bound(odlc_arr, random.randrange(-180,180))


        for key,val in curr_odlc_text_loc.items():
            curr_odlc_text_loc[key] = (
                    int(rot_mat[0,0]*val[0] + rot_mat[0,1]*val[1] + rot_mat[0,2]),
                    int(rot_mat[1,0]*val[0] + rot_mat[1,1]*val[1] + rot_mat[1,2])
                    )

        top_left = random.randint(0, img_arr.shape[0]-odlc_arr.shape[0]), random.randint(0, img_arr.shape[1]-odlc_arr.shape[1])

        if data_format == Formatter.icdar_dataset:
            for key,val in curr_odlc_text_loc.items(): 
                curr_odlc_text_loc[key] = int(val[0] + top_left[0]), int(val[1] + top_left[1])
        
        if DEBUG:
            print((img_arr.shape[0]-odlc_arr.shape[0], img_arr.shape[1]-odlc_arr.shape[1]))
            print(img_arr.shape)
            print(odlc_arr.shape)
            print(top_left)

        if DEBUG: print('putting odlc into image')
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

        if DEBUG:
            cv.imshow('image', img_arr)
            cv.waitKey(0)
            cv.destroyAllWindows()

        img_to_write = img_arr[
                top_left[0]:top_left[0]+odlc_arr.shape[0],
                top_left[1]:top_left[1]+odlc_arr.shape[1]
                ]

        if DEBUG:
            cv.imshow('image '+str(odlc['file_name']), img_to_write)
            cv.waitKey(0)
            cv.destroyAllWindows()
        
        if DEBUG: print('inserting into', str(img_odlc_num) +'.txt')
        with open(os.path.join(cwd, out_dir, str(img_odlc_num) + '.txt'), 'a') as img_file:
            ins_string = ''

            if data_format == Formatter.yolo_dataset:
                ins_string += str(odlc['class_id']) + ','
                for key,val in curr_odlc_text_loc.items():
                    ins_string += str(val[0]/img_to_write.shape[0]) + ',' 
                    ins_string += str(val[1]/img_to_write.shape[1]) + ','
                ins_string += str(odlc['yolo_text']['width']/img_to_write.shape[0]) + ','
                ins_string += str(odlc['yolo_text']['height']/img_to_write.shape[1]) + ','
                ins_string += '\n'
                if DEBUG: print(str(img_odlc_num)+'.txt', ins_string, end='')
                
            elif data_format == Formatter.icdar_dataset:
                for key,val in curr_odlc_text_loc.items():
                    ins_string += str(val[0]) + ',' + str(val[1]) + ','
                ins_string += odlc['alpha_num'] + '\n'
                if DEBUG: print(str(img_odlc_num)+'.txt', ins_string, end='')

            img_file.write(ins_string)

        cv.imwrite(os.path.join(cwd, out_dir, str(img_odlc_num) + '.jpg'), img_to_write)

        if data_format == Formatter.yolo_dataset:
            with open(os.path.join(cwd, 'train.txt'), 'a') as train_file:
                train_file.write(os.path.join(cwd, out_dir, str(img_odlc_num) + '.jpg') + '\n')


        if DEBUG: print('finishing inserting into', str(img_odlc_num) + '.txt')
        with open(os.path.join(cwd, out_dir, str(img_odlc_num) + '.txt'), 'a') as img_file:
            img_file.write('')

        img_odlc_num += 1


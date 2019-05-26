import os
import cv2 as cv
import random
import numpy as np

DEBUG = False

empty_imgs_dir = 'empty_imgs'
flu_odlcs_dir = 'flu_odlcs'
cwd = os.getcwd()
empty_imgs = os.listdir(os.path.join(cwd, empty_imgs_dir))
flu_odlcs = os.listdir(os.path.join(cwd, flu_odlcs_dir))

li = []
for flu_shape in flu_odlcs:
    meta = flu_shape.split('_')
    meta[-1], img_type = meta[-1].split('.')
    meta.append(img_type)
    meta.append(flu_shape)
    li.append(meta)
flu_odlcs = li

for img in empty_imgs:
    img_path = os.path.join(cwd, empty_imgs_dir, img)
    img_arr = cv.imread(img_path)

    added_odlcs = random.sample(flu_odlcs, random.randint(0,len(flu_odlcs)))
    
    for odlc in added_odlcs:
        odlc_path = os.path.join(cwd, flu_odlcs_dir, odlc[-1])

        odlc_arr = cv.imread(odlc_path)
        print(odlc_arr, odlc_arr.shape)
        scale = 8
        odlc_arr = cv.resize(odlc_arr, tuple([int(odlc_arr.shape[0]/scale), int(odlc_arr.shape[1]/scale)]))

        top_left = random.randint(0, img_arr.shape[0]-odlc_arr.shape[0]), random.randint(0, img_arr.shape[1]-odlc_arr.shape[1])
        
        if DEBUG:
            print((img_arr.shape[0]-odlc_arr.shape[0], img_arr.shape[1]-odlc_arr.shape[1]))
            print(img_arr.shape)
            print(odlc_arr.shape)
            print(top_left)

        for col in range(odlc_arr.shape[1]): 
            for row in range(odlc_arr.shape[0]):
                if np.array(odlc_arr[row,col]).sum() < np.array((250,250,250)).sum():
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
        cv.imshow('image'+odlc[-1], img_arr)
        cv.waitKey(0)
        cv.destroyAllWindows()

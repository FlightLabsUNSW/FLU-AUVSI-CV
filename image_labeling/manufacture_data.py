import os
import cv2 as cv

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
        odlc_path = os.path.join(cwd, flu_odlcs_dir, odlc)
        odlc_arr = cv.imread(odlc_path)
        top_left = random.randint(0, img_arr.shape[0]-odlc_arr.shape[0]), random.randint(0, img_arr.shape[1]-odlc_arr.shape[1])
        for row in range(odlc_arr.shape[0]):
            for col in range(odlc_arr.shape[1]):
                if odlc_arr[row,col].sum() < (250,250,250).sum():
                    img_arr[top_left+np.array((row, col))] = odlc_arr[row, col]

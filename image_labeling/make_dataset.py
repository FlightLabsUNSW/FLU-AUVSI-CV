'''
Selects images such that all images are chosen evenly (longer videos are more likely to be chosen from)
Usage:
    python make_dataset.py [image_folder] -n"num_images"
'''

import os, random, argparse

parser = argparse.ArgumentParser(description='Selects images such that all images are chosen evenly (longer videos are more likely to be chosen from)')
parser.add_argument('image_folder')
parser.add_argument('-n', metavar="num_images", default=1000, type=int)
args = parser.parse_args()

image_folder = args.image_folder

all_im = []
for i in os.listdir(image_folder):
    for j in os.listdir(os.path.join(image_folder, i)):
        all_im.append(os.path.join(image_folder, i, j))

dataset = random.sample(all_im, args.n)

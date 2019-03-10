'''
Selects images such that all images are chosen evenly (longer videos are more likely to be chosen from)
'''

import os, shutil, random, argparse

# Tests if a folder exists and makes it if not
def make_folder(folder_path_name):
    try:
        if not os.path.exists(folder_path_name):
            os.makedirs(folder_path_name)
    except OSError:
        sys.exit('Error creating ' + folder_path_name + ' Directory')

parser = argparse.ArgumentParser(description='Selects images such that all images are chosen evenly (longer videos are more likely to be chosen from)')
parser.add_argument('image_folder')
parser.add_argument('-n', metavar="num_images", default=1000, type=int)
parser.add_argument('-d', '--dest', default='dataset')
parser.add_argument('--num_datasets', default=20, type=int)
args = parser.parse_args()

image_folder = args.image_folder

all_im = []
for i in os.listdir(image_folder):
    for j in os.listdir(os.path.join(image_folder, i)):
        all_im.append(os.path.join(image_folder, i, j))

make_folder(args.dest)
for i in range(0, args.num_datasets):
    dataset_folder = os.path.join(args.dest, str(i+1))
    make_folder(dataset_folder)
    dataset = random.sample(all_im, args.n)
    for im_file in dataset:
        shutil.copy(im_file, dataset_folder)

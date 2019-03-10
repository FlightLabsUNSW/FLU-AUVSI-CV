"""
Coverts every video file in video_folder into frames and stores in image_folder
Only tested with .mov and mp4 files
Names them appropriately

Run:
    python3 video_split_to_frames.py image_folder video_folder
"""

import cv2, os, sys

accepted_formats = (".mov", ".mp4")

video_folder = sys.argv[-1]
image_folder = sys.argv[-2]
converted_video_folder = video_folder + "_old"

# Tests if a folder exists and makes it if not
def make_folder(folder_path_name):
    try:
        if not os.path.exists(folder_path_name):
            os.makedirs(folder_path_name)
    except OSError:
        sys.exit('Error creating ' + folder_path_name + ' Directory')

if __name__ == "__main__":
    # Make video and image folders if don't exist
    for folder in [video_folder, image_folder, converted_video_folder]:
        make_folder(folder)
    
    # Convert every videos
    for filename in os.listdir(video_folder):
        low_filename = filename.lower()
        if low_filename.endswith(accepted_formats):
            curr_frame = 0
    
            # Define input file and output folder
            full_file_path = os.path.join(video_folder, filename)
            vid_img_folder = os.path.join(image_folder, filename)
    
            cap = cv2.VideoCapture(full_file_path)
    
            # Create output folder
            make_folder(vid_img_folder)
            
            while (True):
                ret, frame = cap.read()
                if not ret:
                    break
                
                img_name = str(curr_frame) + '.jpg'
                img_path = os.path.join(vid_img_folder, img_name)
    
                print("creating:", img_path)
                cv2.imwrite(img_path, frame)
    
                curr_frame += 1
            cap.release()
            os.rename(full_file_path, os.path.join(converted_video_folder, filename))

Script to split videos into individual images


# Note the dot, is very important
To install:
    $ sudo apt-get python3-virtualenv
    $ virtualenv -p python3 venv
    $ . venv/bin/activate
    $ pip install -r requirments.txt
    $ deactivate

run:
    $ . venv/bin/activate
    $ python video_split_to_frames.py image_folder video_folder
    $ deactivate

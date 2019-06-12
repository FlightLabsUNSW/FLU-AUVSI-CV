
import cv2 as cv
import numpy as np
import os, sys, json
import multiprocessing as mp
import logging
from datetime import datetime

# Initialize the parameters
confThreshold = 0.25  #Confidence threshold
nmsThreshold = 0.4   #Non-maximum suppression threshold
inpWidth = 704       #Width of network's input image
inpHeight = 704      #Height of network's input image

# Give the configuration and weight files for the model and load the network using them.
modelConfiguration = "flu-yolov3-tiny.cfg";

modelWeights1 = "flu-yolov3-tiny_15000.weights";
net1 = cv.dnn.readNetFromDarknet(modelConfiguration, modelWeights1)
net1.setPreferableBackend(cv.dnn.DNN_BACKEND_OPENCV)
net1.setPreferableTarget(cv.dnn.DNN_TARGET_OPENCL)

modelWeights2 = "flu_genobjdetect_1000.weights";
net2 = cv.dnn.readNetFromDarknet(modelConfiguration, modelWeights2)
net2.setPreferableBackend(cv.dnn.DNN_BACKEND_OPENCV)
net2.setPreferableTarget(cv.dnn.DNN_TARGET_OPENCL)


# Get the names of the output layers
def getOutputsNames(net):
    # Get the names of all the layers in the network
    layersNames = net.getLayerNames()
    # Get the names of the output layers, i.e. the layers with unconnected outputs
    return [layersNames[i[0] - 1] for i in net.getUnconnectedOutLayers()]


# Remove the bounding boxes with low confidence using non-maxima suppression
def postprocess(frame, outs, net_type='net1'):
    frameHeight = frame.shape[0]
    frameWidth = frame.shape[1]

    # Scan through all the bounding boxes output from the network and keep only the
    # ones with high confidence scores. Assign the box's class label as the class with the highest score.
    classIds = []
    confidences = []
    boxes = []
    for out in outs:
        for detection in out:
            scores = detection[5:]
            classId = np.argmax(scores)
            confidence = scores[classId]
            if confidence > confThreshold:
                center_x = int(detection[0] * frameWidth)
                center_y = int(detection[1] * frameHeight)
                width = int(detection[2] * frameWidth)
                height = int(detection[3] * frameHeight)
                left = int(center_x - width / 2)
                top = int(center_y - height / 2)
                classIds.append(classId)
                confidences.append(float(confidence))
                boxes.append([left, top, width, height])

    # Perform non maximum suppression to eliminate redundant overlapping boxes with
    # lower confidences.
    detected_objs = []
    indices = cv.dnn.NMSBoxes(boxes, confidences, confThreshold, nmsThreshold)
    for i in indices:
        i = i[0]
        box = boxes[i]
        left = box[0]
        top = box[1]
        width = box[2]
        height = box[3]
        if (classIds[i] == 20 and net_type == 'net1') or (classIds[i] == 0 and net_type == 'net2'):
            ret_cl_id = 'shape'
            detected_objs.append({'class':ret_cl_id, 'confidence':confidences[i], 'left':left, 'top':top, 'right':left + width, 'bottom':top + height})
        elif (classIds[i] == 14 and net_type == 'net1') or (classIds[i] == 1 and net_type == 'net2'):
            ret_cl_id ='person'
            detected_objs.append({'class':ret_cl_id, 'confidence':confidences[i], 'left':left, 'top':top, 'right':left + width, 'bottom':top + height})
    return detected_objs



def classify(frame):
    # Create a 4D blob from a frame.
    blob = cv.dnn.blobFromImage(frame, 1/255, (inpWidth, inpHeight), [0,0,0], 1, crop=False)

    # Sets the input to the network
    net1.setInput(blob)
    net2.setInput(blob)

    # Runs the forward pass to get output of the output layers
    outs1 = net1.forward(getOutputsNames(net1))
    outs2 = net2.forward(getOutputsNames(net2))
    
    # Remove the bounding boxes with low confidence
    detected_objs1 = postprocess(frame, outs1, 'net1')
    detected_objs2 = postprocess(frame, outs2, 'net2')
    return detected_objs1 + detected_objs2

def classify_and_net(frame):
    return classify(frame), net

class Dummy_pipe():
    def send(self, data_in):
        return

    def recv(self):
        return True

default_vids = [0,1]

def run_classification(data_pipe, cmd_pipe=Dummy_pipe(), vid_names=default_vids):
    caps = []
    done = []
    for vid in vid_names:
        caps.append(cv.VideoCapture(vid))
        done.append(False)

    cmd_pipe.send({'not_started':1})
    while not cmd_pipe.recv().get('run'):
        continue
    cmd_pipe.send({'started':1})

    all_done = False
    while not all_done:
        for cap_i, cap in enumerate(caps):
            if done[cap_i]:
                has_img, img = cap.read()
                read_time = datetime.now().timestamp()
                if not has_img:
                    cap.release()
                    cmd_pipe.send({'finished':1})
                    done[cap_i] = True
                else:
                    found_objs = classify(img)
                    obj_detected = {}
                    obj_detected['image'] = img
                    obj_detected['objects'] = found_objs
                    obj_detected['time_taken'] = read_time

                    for detection in obj_detected['objects']:
                        cropped_img = classifications['image'][detection['left']:detection['right'],detection['top']:detection['bottom']]
                        cv.imwrite(os.path.join(out_folder, str(obj_id)+'.jpg'), cropped_img)

                        obj_metadata = {
                                'time_taken':classifications['time_taken'],
                                'detection_data':detection
                                }
                        
                        with open(os.path.join(out_folder, str(obj_id)+'.json'), 'w') as obj_fi:
                            json.dump(obj_fi, obj_metadata)

                    data_pipe.send(obj_detected)
                    cmd_pipe.send({'object_sent':1})
        all_done = True
        for cap_d in done:
            if not cap_d:
                all_done = False
        while cmd_pipe.poll():
            cmd_val = cmd_pipe.recv()
            if cmd_val.get('finish'):
                cmd_pipe.send({'finishing':1})
                all_done = True
    #redundant from Process.join() but still do it anyway
    cmd_pipe.send({'done':1})

# Tests if a folder exists and makes it if not
def make_folder(folder_path_name):
    try:
        if not os.path.exists(folder_path_name):
            os.makedirs(folder_path_name)
    except OSError as err:
        print(err)
        sys.exit('Error creating ' + folder_path_name + ' Directory')

if __name__ == "__main__":
    vid_input = sys.argv[-1] if len(sys.argv) > 1 else default_vids

    out_folder = 'out_objs'
    make_folder(out_folder)

    logging_dev = logging.getLogger("run_out")
    logging_dev.setLevel(logging.DEBUG)
    fh = logging.FileHandler("rp_out.log")
    fh.setLevel(logging.DEBUG)
    logging_dev.addHandler(fh)

    cmd_pipe_parent, cmd_pipe_child = mp.Pipe()
    data_pipe_parent, data_pipe_child = mp.Pipe()
    real_proc = mp.Process(target=run_classification, args=(data_pipe_child, cmd_pipe_child, vid_input))
    real_proc.start()

    done = False
    obj_id = 0
    while not done:
        cmd = input(">>> ")
        if cmd == "finish":
            done = True
        cmd_pipe_parent.send({cmd:1})
        while cmd_pipe_parent.poll():
            logging_dev.debug(cmd_pipe_parent.recv())

        while data_pipe_parent.poll():
            classifications = data_pipe_parent.recv()
            for detection in classifications['objects']:
                cropped_img = classifications['image'][detection['left']:detection['right'],detection['top']:detection['bottom']]
                cv.imwrite(os.path.join(out_folder, str(obj_id)+'.jpg'), cropped_img)

                obj_metadata = {
                        'time_taken':classifications['time_taken'],
                        'detection_data':detection
                        }
                
                logging_dev.debug(json.dumps(obj_metadata, iindent=4))
    waiting = False
    while waiting:
        info = cmd_pipe_parent.recv()
        if info.get('done'):
            waiting = True
        logging_dev.debug(info)
    print('ending')
    real_proc.join()


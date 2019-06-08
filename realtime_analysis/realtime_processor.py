
import cv2 as cv
import numpy as np
import os, sys
from datetime import datetime

# Initialize the parameters
confThreshold = 0.5  #Confidence threshold
nmsThreshold = 0.4   #Non-maximum suppression threshold
inpWidth = 416       #Width of network's input image
inpHeight = 416      #Height of network's input image

# Give the configuration and weight files for the model and load the network using them.
modelConfiguration = "flu-yolov3-tiny.cfg";
modelWeights = "flu-yolov3-tiny_1000.weights";

net = cv.dnn.readNetFromDarknet(modelConfiguration, modelWeights)
net.setPreferableBackend(cv.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv.dnn.DNN_TARGET_OPENCL)


# Get the names of the output layers
def getOutputsNames(net):
    # Get the names of all the layers in the network
    layersNames = net.getLayerNames()
    # Get the names of the output layers, i.e. the layers with unconnected outputs
    return [layersNames[i[0] - 1] for i in net.getUnconnectedOutLayers()]


# Remove the bounding boxes with low confidence using non-maxima suppression
def postprocess(frame, outs):
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
        detected_objs.append({'class':classIds[i], 'confidence':confidences[i], 'left':left, 'top':top, 'right':left + width, 'bottom':top + height})
    return detected_objs



def classify(frame):
    # Create a 4D blob from a frame.
    blob = cv.dnn.blobFromImage(frame, 1/255, (inpWidth, inpHeight), [0,0,0], 1, crop=False)

    # Sets the input to the network
    net.setInput(blob)

    # Runs the forward pass to get output of the output layers
    outs = net.forward(getOutputsNames(net))

    # Remove the bounding boxes with low confidence
    return postprocess(frame, outs)

class Dummy_pipe():
    def send(self, data_in):
        return

    def recv(self):
        return True

def run_classification(data_pipe, cmd_pipe=Dummy_pipe(), vid_names=default_vids):
    caps = []
    done = []
    for vid in vid_names:
        caps.append(cv.VideoCapture(vid_name))
        done.append(False)

    #while not cmd_pipe.recv()['run']:
    #    continue
    cmd_pipe.send({'started':1})

    while not all_done:
        for cap_i, cap in enumerate(caps):
            if done[cap_i]:
                has_img, img = cap.read()
                read_time = datetime.now().timestamp()
                if not has_img:
                    cap.release()
                    cmd_pip.send({'finished':1})
                    done[cap_i] = True
                else:
                    found_objs = classify(img)
                    obj_detected = {}
                    obj_detected['image'] = img
                    obj_detected['objects'] = found_objs
                    obj_detected['time_taken'] = read_time

                    data_pipe.send(obj_detected)
                    cmd_pipe.send({'object_sent':1})
        all_done = True
        for cap_d in done:
            if not cap_d:
                all_done = False

    #redundant from Process.join() but still do it anyway
    cmd_pipe.send({'done':1})

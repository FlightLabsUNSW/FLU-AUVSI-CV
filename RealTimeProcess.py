import cv2
import pickle

def real_time_process(conn):
	while True:
		image = cv2.imread("test2.png")

		capture = {
			"image": image,
			"objects": [
				{ "class": "shape", "confidence": 0.9, "left": 0, "top": 100, "right": 100, "bottom": 0 },
				{ "class": "shape", "confidence": 0.9, "left": 400, "top": 500, "right": 500, "bottom": 400 }
			]
		}

		conn.send(capture)
	

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

                        obj_id += 1

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
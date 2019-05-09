import multiprocessing as mp
import time
import logging
import os
import cv2 as cv

def run_proc(cmd_ch, frame_ch):
    logging_dev = logging.getLogger("run_out")
    vid_cap = cv.VideoCapture("run.mp4")
    frame = None
    not_exit = True
    while not_exit:
        cmd = cmd_ch.recv()
        if (cmd.get("hello")):
            logging_dev.debug("Hi there from subproc")
        elif (cmd.get("get_frame")):
            logging_dev.debug("load a frame into memory from video")
            ret_val, frame = vid_cap.read()
            logging_dev.debug(str(frame))
        elif (cmd.get("send_frame")):
            frame_ch.send(frame)
        elif (cmd.get("check_pid")):
            logging_dev.debug(os.getpid())
        elif (cmd.get("shutdown")):
            logging_dev.debug("Exiting subproc")
            not_exit = False
        else:
            logging_dev.debug(str(cmd))
    return

if __name__ == "__main__":
    com_ch = mp.Pipe()
    vid_link = mp.Pipe(duplex=False)
    frame_out = vid_link[0]
    subp = mp.Process(target=run_proc, args=(com_ch[0], vid_link[1]))

    subproc_logger = logging.getLogger("run_out")
    subproc_logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler("subp_out.log")
    fh.setLevel(logging.DEBUG)
    subproc_logger.addHandler(fh)
    
    subp.start()
    not_done = True
    while not_done:
        cmd_in = input("Enter command to subprocess\n")
        cmd_msg = {cmd_in:1}
        com_ch[1].send(cmd_msg)

        if frame_out.poll():
            ret_msg = frame_out.recv()
            print(str(ret_msg))

        if (cmd_in == "shutdown"):
            not_done = False
        elif (cmd_in == "check_pid"):
            print(os.getpid())
    subp.join()

import multiprocessing as mp
import time
import logging

def run_proc(cmd_ch):
    logging_dev = logging.getLogger("run_out")
    logging_dev.setLevel(logging.DEBUG)
    fh = logging.FileHandler("subp_out.log")
    fh.setLevel(logging.DEBUG)
    logging_dev.addHandler(fh)
    not_exit = True
    while not_exit:
        cmd = cmd_ch.recv()
        if (cmd == "hello"):
            logging_dev.debug("Hi there from subproc")
        elif (cmd == "count"):
            pr_li = [i for i in range(10)]
            logging_dev.debug(pr_li)
        elif (cmd == "shutdown"):
            logging_dev.debug("Exiting subproc")
            not_exit = False
        else:
            logging_dev.debug(cmd)
    return

if __name__ == "__main__":
    com_ch = mp.Pipe()
    subp = mp.Process(target=run_proc, args=(com_ch[0],))
    
    subp.start()
    not_done = True
    while not_done:
        cmd_in = input("Enter command to subprocess\n")
        com_ch[1].send(cmd_in)

        if (cmd_in == "shutdown"):
            not_done = False
    subp.join()

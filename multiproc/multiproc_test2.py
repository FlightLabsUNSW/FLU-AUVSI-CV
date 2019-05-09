import multiprocessing as mp
from ctypes import c_bool

class CV_manager:
    def __init__(self, num_processors, shutdown_signal):
        self.realtime_detect = CV_realtime_detector(shutdown_signal)
        self.processors = [ CV_processor(shutdown_signal) for i in range(num_processors)]
        self.shutdown_signal = shutdown_signal

    def begin_man(self, name):
        print("Starting Manager Proc")
        a = mp.Process(target=CV_realtime_detector.begin_real, args=(self.realtime_detect, 'r_d'))
        a.start()
        b = [mp.Process(target=CV_processor.begin_process, args=(i, 's')) for i in self.processors]
        for j in b:
            j.start()
        i = 0
        while (not self.shutdown_signal.poll()):
            i += 1
        a.join()
        for j in b:
            j.join()
        print("Ending Manager Proc")

class CV_realtime_detector:
    def __init__(self, shutdown_signal):
        self.shutdown_signal = shutdown_signal

    def begin_real(self, name):
        print("Starting Realtime Proc")
        i = 0
        while (not self.shutdown_signal.poll()):
            i += 1
        print("Ending Realtime Proc")


class CV_processor:
    def __init__(self, shutdown_signal):
        self.shutdown_signal = shutdown_signal

    def begin_process(self, name):
        print("Starting Processor Proc")
        i = 0
        while (not self.shutdown_signal.poll()):
            i += 1
        print("Ending Processor Proc")

if __name__ == "__main__":
    #shutdown_signal = mp.Value(c_bool, False)
    shutdown_signal, shutdown_send = mp.Pipe()
    man_obj = CV_manager(5, shutdown_signal)
    manager_proc = mp.Process(target=CV_manager.begin_man, args=(man_obj, 'manager'))
    cmd = None
    while (cmd != "s"):
        cmd = input(">>> ")
    manager_proc.start()
    
    while (cmd != "q"):
        cmd = input(">>> ")

    #shutdown_signal = True
    shutdown_send.send("shutdown")
    manager_proc.join()

    print("Fully Shutdown")

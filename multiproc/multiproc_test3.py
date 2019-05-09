import multiprocessing as mp
from ctypes import c_bool

class int_obj:
    def __init__(self, _snapshot_time, _image_link, _location):
        self.obj_id=0
        self.snapshot_time =_snapshot_time
        self.image_link = _image_link
        self. location = _location


class int_obj_database:
    def __init__(self, _int_obj=[], _proc_pool=mp.Pool()):
        self.int_obj = _int_obj
        self.proc_pool = _proc_pool

if __name__ == "__main__":
    gen_obj_pipe = mp.Pipe()
    start_and_run_GOD_proc(gen_obj_pipe)
    while True:
        obj_batch = []
        while (len(obj_batch_list) <= batch_num_thresh):
            obj_batch.append(gen_obj_pipe.recv())
        
        int_obj_list = analysis_proc_pool.starmap(int_obj, obj_batch)
        int_obj_list = analysis_proc_pool.starmap(calc_location, int_obj_list)

import multiprocessing as mp


def worker(i, queue, new_str):
    """worker function"""
    print(new_str, i)
    to_add =  'Extracting  Worker ' + str(i)
    queue.put(to_add)
    print('End', i)
    return to_add

if __name__ == '__main__':
    num_proc = 5
    jobs = []
    q = mp.Queue()
    for i in range(num_proc):
        p = mp.Process(target=worker, args=(i, q, "Start"))
        jobs.append(p)
        p.start()
    for i in range(num_proc):
        print(q.get())
    for task in jobs:
        print('waiting for task to finish')
        task.join()

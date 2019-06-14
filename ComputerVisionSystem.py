from Manager         import Manager
from multiprocessing import Process, Value

stop_manager = Value('i', 0)

system = Manager(stop_manager)

manager_process = Process(target=system.run)

manager_process.start()

while True:
	command = input()

	if (command == "stop"):
		stop_manager.value = 1
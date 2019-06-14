#import rospy
#from sensor_msgs.msg import Imu

from datetime import datetime
import time

class Data:
	def __init__(self):
		self.angular_position = {
			"x_angle": 0,
			"y_angle": 0
		}

		self.global_position = {
			"latitude":    0,
			"longitude":   0,
			"compass_hdg": 90,
			"rel_alt":     100
		}

class Telemetry:
	def __init__(self, pipe1, pipe2):
		self.pipe1 = pipe1 # Manager process pipe, used to clear data
		self.pipe2 = pipe2 # Pipe to send data to manager process

	def callback(self, data):
	    #rospy.loginfo(rospy.get_caller_id() + "\nlinear acceleration:\nx: [{}]\ny: [{}]\nz: [{}]".
	    #format(data.linear_acceleration.x, data.linear_acceleration.y, data.linear_acceleration.z))

	    # Clear pipe
	    #while (self.pipe1.poll()):
	    #	self.pipe1.recv()

	    self.pipe2.send({"time": datetime.utcnow(), "data": data})

	def listen(self):
		#rospy.init_node('listener', anonymous=True)
		#rospy.Subscriber("/mavros/imu/data", Imu, self.callback)
		#rospy.spin()
		
		data = Data()

		while True:
			self.callback(data)
			time.sleep(0.5)

if __name__ == '__main__':
	telemetry = Telemetry()

	telemetry.listen()
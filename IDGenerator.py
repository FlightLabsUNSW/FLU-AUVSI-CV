class IDGenerator:
	def __init__(self):
		self.current_id = 0

	def get_id(self):
		self.current_id += 1
		return self.current_id



class PID:
	'''
		
		Simple Class serving as a virtual PID lockbox using first order
		approximations for integration and derivatives.

	'''

	#memory variables
	# integrator	= 0
	last_error	= None

	#gain values 
	proportional	= 0
	integral    	= 0
	derivative  	= 0
	total_gain  	= 1

	#output vars
	output = 0

	def __init__(self):
		self.integrator = 0
		
	def loop(self, error, dt):
		'''
			Updates output using PID algorithm.
		'''

		#calculate derivative if and only if this is not the first call
		if last_error != None:
			derivate_error = (error - self.last_error)/dt
			self.last_error = error

		#integrate
		self.integrator += error*dt

		#calculate output
		self.output	= 	proportional*error
		self.output	+=	integral*integrated_error
		self.output	+=	derivate_error 

		return total_gain*output

	def test_mem(self):
		self.integrator += 1

		print(self.integrator)
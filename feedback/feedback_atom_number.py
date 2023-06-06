'''
	Feedbacks atom number with oven current.
'''

import runmanager.remote as remote
from lyse import *
import os
import pprint
import numpy as np
import math

invert	= False
I     	= 1
_min  	= -0.1
_max  	= 0

def get_atom_number(df, parameters=None):
	print("Getting atom number...")
	#post select
	rg = remote.get_globals(raw=True)
	desired_atom_number = eval(rg['desired_atom_number'])
	print("desired_atom_number: ", desired_atom_number)
	# c1 = df['cavity_scan_analysis', 'Neta_3'] + df['cavity_scan_analysis', 'Neta_4'] > desired_atom_number/2
	# df = df[c1]
	Neta_3 = array(df['cavity_scan_analysis', 'Neta_3'])
	Neta_4 = array(df['cavity_scan_analysis', 'Neta_4'])

	return np.nanmean(Neta_4 + Neta_3)

class PIDFeedback():
	def __init__(self, G=0,P=0,_min=0,_max=0,setpoint=0):
		''' define PID parameters '''
		print("Initializing PID Loop")
		self.G = G
		self.P = P
		self._min = _min
		self._max = _max
		self.setpoint = setpoint
	def set_error(self, input):
		self.error = input - self.setpoint
	def get_output(self, output):
		initial_output = output
		output += -self.G*self.P*self.error

		if output < self._min or output > self._max:
			print(f"Warning: Feedback seems out of lock... Near boundaries [{self._min},{self._max}]")
			return initial_output
		elif not math.isnan(output):
			return output
		return initial_output

def main():
	import math

	MHz = 1e6

	rg = remote.get_globals(raw=True)

	LOCK_ATOM_NUMBER = eval(rg['LOCK_ATOM_NUMBER'])
	OVEN_IS_ON = eval(rg['TURN_ON_OVEN'])
	print(f"LOCK_ATOM_NUMBER: {repr(LOCK_ATOM_NUMBER)}")
	if  (not LOCK_ATOM_NUMBER) or (not OVEN_IS_ON) or (remote.n_shots() != 1):
		print("Don't lock atom number.")
		return
	try:
		
		#feedback on last 10 shots
		df = data(n_sequences=10)

		atom_number = get_atom_number(df)
		print("Detected Atom Number: ", atom_number)
		pi = PIDFeedback(
				G       	= float(rg['atom_loading_G']),
				P       	= float(rg['atom_loading_P']),
				setpoint	= float(rg['desired_atom_number']),
				_min    	= float(rg['min_oven_current']),
				_max    	= float(rg['max_oven_current'])
			)

		pi.set_error(input=atom_number)
		print("Error: ", pi.error)
		print("Feedback: ", -pi.G*pi.P*pi.error)
		output = pi.get_output(output = float(rg['fb_oven_current']))

		globals_to_set = {"fb_oven_current": output}


		#update the global variables
		print("Setting Global Variables...")
		print(output)
		remote.set_globals(globals_to_set)
		# print(output)
		print("Succesfully Performed Feedback.")
	except Exception as e:
		import traceback
		import sys

		print(f"Failed Feedback:")
		traceback.print_exception(*sys.exc_info())

if __name__ == '__main__':
	main()

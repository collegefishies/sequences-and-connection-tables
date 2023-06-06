'''

	Changes the HP8648 Frequency so that the ExperimentalCavity frequency shows
	up at the appropriate location.

	This will use a simple PID loop.

'''
import runmanager.remote as remote
from lyse import data, Run
import os
import pprint
from labscriptlib.ybclock.analysis.scripts import repack_globals
import numpy as np
from numpy import array
def get_frequency_df():
	df = data(n_sequences=10)
	return np.nanmean(array(df['empty_cavity_helper','exp_cavity_frequency']))
def get_frequency_single_shot():
	run = Run(path)
	actual_cavity_frequency = run.get_result('empty_cavity_helper','exp_cavity_frequency')
	return actual_cavity_frequency
def main():
	import math
	#make sure the .ini config file has the correct address for the Runmanager!!!

	MHz = 1e6

	if remote.n_shots() != 1:
		print("Too many shots not feeding back.")
		return

	try:
		#read cavity frequency
		print("Reading Cavity Frequency...")

		
		actual_cavity_frequency = get_frequency_df()


		print("Performing Feedback & Getting Globals...")
		#get PID variables
		retrieved_globals = remote.get_globals(raw=True)
		# pprint.pprint(retrieved_globals)
		empty_cavity_set_frequency = float(eval(retrieved_globals['empty_cavity_set_frequency']))
		LOCK_ATOM_NUMBER = bool(retrieved_globals['LOCK_ATOM_NUMBER'])
		dispersive_shift_per_Neta = float(retrieved_globals['dispersive_shift_per_Neta'])
		desired_atom_number = float(retrieved_globals['desired_atom_number'])
		f_atoms = float(eval(retrieved_globals['f_atoms']))
		G             	= float(retrieved_globals['cavity_frequency_G'])
		I             	= float(retrieved_globals['cavity_frequency_I'])
		P             	= float(retrieved_globals['cavity_frequency_P'])
		integrator    	= float(retrieved_globals['cavity_frequency_integrator'])
		_min          	= float(retrieved_globals['min_bridging_frequency_759'])
		_max          	= float(retrieved_globals['max_bridging_frequency_759'])
		QUICK_FEEDBACK	= bool(eval(retrieved_globals['QUICK_FEEDBACK']))
		SAFE_FEEDBACK 	= bool(eval(retrieved_globals['SAFE_FEEDBACK']))

		if QUICK_FEEDBACK:
			G *= 10
		#read desired setpoint
		setpoint	= float(eval(retrieved_globals['exp_cavity_set_frequency']))

		#check to see if the frequency isn't abnormally far from the setpoint
		#engage next shot anyways
		MHz = 1.
		safe_distance = 3*MHz
		print(SAFE_FEEDBACK)
		if SAFE_FEEDBACK and (abs(actual_cavity_frequency - setpoint) > safe_distance):
			print(f"Frequency is too far {safe_distance} MHz from setpoint . Aborting.")
			return

		#perform PID
		error = actual_cavity_frequency - setpoint

		output = -G*(P*error)

		#set cavity frequency 
		temp_bridging_frequency = float(retrieved_globals['bridging_frequency_759'])
		temp_bridging_frequency -= output

		if temp_bridging_frequency < _min or temp_bridging_frequency > _max:
			print(f"Warning: Feedback seems out of lock... Near boundarys [{_min},{_max}]")
		elif not math.isnan(temp_bridging_frequency):
			retrieved_globals['bridging_frequency_759'] = str(temp_bridging_frequency)

			#update the global variables
			print("Setting Global Variables...")
			remote.set_globals(retrieved_globals, raw=True)

		#engage the next shot.
		# print("repack_globals...")
		# repack_globals(
		#	[
		#		"globals",
		#		"cavity_globals",
		#		"optimization",
		#		"working_globals"
		#	]
		# )
		print("Engaging Next Shot...", end='')
		# remote.engage()
		print("Done!")
		print("Succesfully Performed Feedback.")
	except Exception as e:
		import traceback
		import sys

		print(f"Failed Feedback:")
		traceback.print_exception(*sys.exc_info())
		#engage the next shot.
		# print("Engaging Next Shot...", end='')
		# repack_globals(
		#	[
		#		"globals",
		#		"cavity_globals",
		#		"optimization",
		#		"working_globals"
		#	]
		# )
		# remote.engage()
		print("Done!")

		pass

if __name__ == '__main__':
	main()
from math import pi

from labscript import start, stop, AnalogOut, DigitalOut, add_time_marker
from labscriptlib.ybclock.connection_table import define_connection_table
from labscriptlib.ybclock.subsequences import *
from labscript_utils.unitconversions import *
from labscriptlib.ybclock.classes import *

if __name__ == '__main__':
	define_connection_table()
	define_classes()


	ms = 1e-3
	us = 1e-6
	kHz = 1e3
	t = 0

	# Begin issuing labscript primitives
	# start() elicits the commencement of the shot


	start()

	t += set_start_values(t + 6*ms)
	t += 10*ms
		

	#calibration
	for i in range(3):
		t += exp_cavity.scan(t,label=f'empty_cavity')
		t += 10*ms	

	t += set_end_values(t)
	t += 10*ms
	stop(t)

print("Compiled test_empty_cavity_scan!")
'''
We measure the cavity lifetime

we don't load atoms
'''

from labscript import start, stop, AnalogOut, DigitalOut,add_time_marker
from labscriptlib.ybclock.connection_table import define_connection_table
from labscriptlib.ybclock.subsequences import *
from labscriptlib.ybclock.classes import define_classes

if __name__ == '__main__':

	ms = 1e-3
	us = 1e-6
	kHz = 1e3

	define_connection_table()
	define_classes()
	HP8648Cfor759.constant(bridging_frequency_759)

	# Begin issuing labscript primitives
	# start() elicits the commencement of the shot
	start()

	t = 10*us
	set_start_values(t)

	# We don't need atoms, but this loading sequence will set all the right frequencies 9in particular the green doublepass) Moreover, it helps with systemxstability
	t += load_from_oven_to_optical_lattice(t,add_marker = True)

	#perform an empty cavity scan
	t += empty_then_measure_cavity_frequency(t)

	t += 20*ms

	# Perform cavity ring down.
	print(f'Time buildup cavity: {t}')
	t += exp_cavity.ringdown(t, label='empty_cavity_ringdown')

	set_end_values(t)
	# Stop the experiment shot with stop()
	stop(t+0.1)

print("Compiled loading_sequence!")

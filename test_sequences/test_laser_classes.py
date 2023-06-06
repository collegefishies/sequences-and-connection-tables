'''
	Example usage for classes. This is also a development tool for myself.
'''

from labscript import start, stop,add_time_marker
from labscriptlib.ybclock.connection_table import define_connection_table
from labscriptlib.ybclock.classes import *
from labscriptlib.ybclock.subsequences import *


ms = 1e-3
dt = 500*ms

if __name__ == '__main__':
	define_connection_table()
	define_classes()
	HP8648Cfor759.constant(bridging_frequency_759)


	# Begin issuing labscript primitives
	# start() elicits the commencement of the shot
	start(); t = 0;
	t += set_start_values()

	# t += wait(10)
	for i in range(10):
		t += 500*ms	
		add_time_marker(t, label='Turn On')
		UNUSED_1.enable(t)
		t += green.pump.intensity.turnon(t, value=0.36)
		# green_mot_shutter.enable(t)
		t += dt
		# green_mot_shutter.disable(t)
		UNUSED_1.disable(t)
		t += green.pump.turnoff(t, warmup_value = 0)


	t += set_end_values(t)
	stop(t+1)

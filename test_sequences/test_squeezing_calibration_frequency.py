from labscript import start, stop,add_time_marker
from labscriptlib.ybclock.connection_table import define_connection_table
from labscriptlib.ybclock.classes import *
from labscriptlib.ybclock.subsequences import *
from labscriptlib.ybclock.subsequences.squeezing import squeezing_pulse


if __name__ == '__main__':
	define_connection_table()
	define_classes()
	HP8648Cfor759.constant(bridging_frequency_759)


	# Begin issuing labscript primitives
	# start() elicits the commencement of the shot
	start(); t = 0;
	t += set_start_values()
	#close the photon counter
	photon_counter_shutter.disable(t)

	#set green frequency to 
	FPGA_DDS9.constant(
		t=t,
		channel=(0b0001),
		value=('freq', green_laser_frequency, 'MHz'),
		description='reference'
		)

	t += 0.1

	t += squeezing_pulse(
		t=t,
		detuning_MHz=10, 
		squeezing_strength_V=1.3,
		duration=1)
	t += 10*ms
	t += squeezing_pulse(
		t=t,
		detuning_MHz=0, 
		squeezing_strength_V=1.3,
		duration=1)
	t += 10*ms

	t += squeezing_pulse(
		t=t,
		detuning_MHz=5, 
		squeezing_strength_V=1.3,
		duration=1)
	t += 10*ms

	green.probe.frequency.constant(t,value=0)
	green.probe.intensity.constant(t, value=1.3)

	t += 1
	t += set_end_values(t)
	stop(t+0.1)

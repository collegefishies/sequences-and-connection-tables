from labscript import start, stop
from labscriptlib.ybclock.connection_table import define_connection_table
from labscriptlib.ybclock.subsequences import *
from labscriptlib.ybclock.classes import define_classes


ms = 1e-3


if __name__ == '__main__':
	define_connection_table()
	define_classes()
	HP8648Cfor759.constant(bridging_frequency_759)
	# Begin issuing labscript primitives
	# start() elicits the commencement of the shot
	start()
	t = 0
	set_start_values()

	shutter_list = [
		probe_sideband_shutter,
		cooling_pi_shutter,
		cooling_sigma_shutter,
		blue_mot_shutter,
		imaging_power_shutter,
		# probe_shutter,
		green_mot_shutter,
		# photon_counter_shutter
	]

	for i in range(10):
		t += wait(250*ms)
		for shutter in shutter_list:
			shutter.disable(t)
		t += wait(250*ms)
		for shutter in shutter_list:
			shutter.enable(t)


	set_end_values(t)
	stop(t+30*ms)

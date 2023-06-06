from labscript import start, stop,add_time_marker
from labscriptlib.ybclock.connection_table import define_connection_table
from labscriptlib.ybclock.classes import *
from labscriptlib.ybclock.subsequences import *


if __name__ == '__main__':
	define_connection_table()
	define_classes()
	HP8648Cfor759.constant(bridging_frequency_759)


	# Begin issuing labscript primitives
	# start() elicits the commencement of the shot
	start(); t = 0;
	t += set_start_values()



	t += set_end_values(t)
	stop(t+1)

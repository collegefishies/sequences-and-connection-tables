from labscript import start, stop, AnalogOut, DigitalOut
from labscriptlib.ybclock.connection_table import define_connection_table
from labscriptlib.ybclock.classes import *
from labscriptlib.ybclock.subsequences import *

if __name__ == '__main__':

	define_connection_table()
	define_classes()
	
	exp_cavity = ExperimentalCavity()
	HP8648Cfor759.constant(bridging_frequency_759)

	# Begin issuing labscript primitives
	# start() elicits the commencement of the shot
	start()
	set_start_values()

	ms = 1e-3
	kHz = 1e3
	t = 0.1

	#take a background image just after turning on beams.
	#load the atoms
	t += blue_mot(t, duration=LS_blue_mot_duration, take_picture=True)
	
	#calibration
	for i in range(1):
		t += exp_cavity.scan(t,label=f'empty_cavity')	


	# Stop the experiment shot with stop()
	set_end_values(t+1*ms)
	stop(t+1)

print("Compiled test_blue_mot!")

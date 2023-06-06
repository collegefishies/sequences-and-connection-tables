from labscript import start, stop, AnalogOut, DigitalOut
from labscriptlib.ybclock.connection_table import define_connection_table
from labscriptlib.ybclock.subsequences import *
from labscriptlib.ybclock.classes import define_classes


if __name__ == '__main__':

	define_connection_table()
	define_classes()
	
	# Begin issuing labscript primitives
	# start() elicits the commencement of the shot
	start()
	set_start_values()

	ms = 1e-3
	kHz = 1e3
	t = 0.1*ms


	#load the atoms
	t += blue_mot(t,                      	duration= 3000*ms, take_picture=True)
	t += transfer_blue_mot_to_green_mot(t,	duration= 40*ms,	samplerate=1*kHz)
	t += transfer_to_triplet_mot(t,
	                                           	freq_ramp_duration= 80*ms,
	                                           	intensity_ramp_duration=40*ms,
	                                           	hold_time=0*ms,
	                                           	samplerate=1*kHz, add_marker=False)
	# t += position_atoms_to_optical_lattice(t,	duration= 40*ms,	samplerate=1*kHz)

	#take a picture of the atoms
	add_time_marker(t+20*ms, "Take Picture of Green MOT", verbose=True)
	isometric_cam.expose(t + 20*ms,	name='green_mot', frametype='signal', trigger_duration=20*ms)

	t += hold_atoms(t,	duration= 40*ms)

	# Stop the experiment shot with stop()
	set_end_values(t+75*ms)
	stop(t+1)

print("Compiled loading_sequence!")

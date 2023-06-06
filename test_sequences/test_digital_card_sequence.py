from labscript import start, stop, add_time_marker, AnalogOut, DigitalOut
from labscriptlib.ybclock.connection_table import define_connection_table

if __name__ == '__main__':

	define_connection_table()
	
	# Begin issuing labscript primitives
	# start() elicits the commencement of the shot
	start()

	t = 0.5 
	green_mot_shutter.enable(t);

	t = 0.7
	green_mot_shutter.disable(t);
	
	# Stop the experiment shot with stop()
	stop(t)
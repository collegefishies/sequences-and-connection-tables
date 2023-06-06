from labscript import start, stop
from labscriptlib.ybclock.connection_table import define_connection_table

if __name__ == '__main__':
	define_connection_table()
	# Begin issuing labscript primitives
	# start() elicits the commencement of the shot
	start()

	HP8648Cfor759.constant(frequency_MHz=400)

	stop(1)

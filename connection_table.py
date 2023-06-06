'''
	A connection table is what labscript calls the settings that define how our hardware is wired up.

	Labscript requires this file with this name so that it can compile what it
	needs for BLACS.

	Since it's name suggests this is also where we get our connection table, I 
	also took the liberty to define the `define_connection_table()` function here
	for easy import into other sequences.

	The bulk of the actual connections is in the `connection_functions` module.
'''

from labscript import start, stop

from labscriptlib.ybclock.connection_functions import define_hardware_cards
from labscriptlib.ybclock.connection_functions import define_channels

def define_connection_table():
	''' Here we break out the connection table into smaller function calls,
	which are in turn broken up and held in connection_functions module.
	This allows for conceptual partitioning and easier navigation of the code.

	More crucially, it's necessary for allowing importation into other sequences.

	I faced problems without defining this function. `define_connection_table`
	needs to be called in the `example_sequence.py` runmanager is compiling.

	The problem is when compiling multiple shots, each time you do  'from
	connection_table import *` it won't run each of the device/channel declaration
	functions again, and so you would need to reset each compiler instance if you
	wanted to run another shot.

	With the function call format, it allows you to run the device/channel
	declaration everytime you compile, as desired.
	'''

	define_hardware_cards()
	
	define_channels()

	#the labscript compiler spits out time markers defined in the main sequence.
	#this is to add text that should have been included in the main labscript
	#compiler.
	print("Time Markers:")



if __name__ == '__main__':

	define_connection_table()
	
	# Begin issuing labscript primitives
	# start() elicits the commencement of the shot
	start()

	# Stop the experiment shot with stop()
	stop(1.0)

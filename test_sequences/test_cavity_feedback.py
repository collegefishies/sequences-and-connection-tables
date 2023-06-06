from labscript import start, stop, AnalogOut, DigitalOut
from labscriptlib.ybclock.connection_table import define_connection_table
from labscriptlib.ybclock.subsequences import *
from labscript_utils.unitconversions import *
from labscriptlib.ybclock.classes import *

us = 1E-6
if __name__ == '__main__':
	define_connection_table()
	define_classes()
	HP8648Cfor759.constant(bridging_frequency_759)

	# Begin issuing labscript primitives
	# start() elicits the commencement of the shot
	start()

	set_default_values()
	t = 1e-3
	FPGA_DDS9.triggerSet(10*us)
	green_frequency_fpga_trigger.enable(10*us)
	FPGA_DDS9.constant(
		t=t,
		channel=(0b0001),
		value=('freq', green_laser_frequency, 'MHz'),
		description='initial value'
		)
	FPGA_DDS9.constant(
		t=t+10*us,
		channel=0b0001,
		value=('ampl',0.5,'1'),
		description='initial value'
		)

	ms = 1e-3
	us = 1e-6
	kHz = 1e3
	t = 200*ms


	#calibration
	for i in range(1):
		t += exp_cavity.scan(t,label=f'empty_cavity')	

	set_default_values(t+1*ms)
	stop(t+1000*ms)

print("Compiled test_empty_cavity_scan!")
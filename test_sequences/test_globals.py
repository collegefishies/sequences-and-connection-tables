'''
The idea is to define global variables in runmanager, and call them here!

For example: it would be useful and practical to be able to define ramp parameters for Rabi scan in globals like:
	`frequency_range = (0, 25) #MHz` (this one can/could be set also in voltage)
	`ramp_speed = 10 #ms`
	`freq_resolution = 10 #kHz`
	`scan_power = 3# V`

In this dummy code, we test the import of globals from runmanager to the sequence.
'''

from labscript_devices.DummyPseudoclock.labscript_devices import DummyPseudoclock
from labscript import start, stop, AnalogOut, DigitalOut
from labscriptlib.ybclock.subsequences import *


if __name__ == '__main__':
	DummyPseudoclock('pseudoclock')

	start()
	ms = 1e-3
	us = 1e-6
	kHz = 1e3
	t = 1*ms

	try:
		print(Rabi_sweep_range)
	except Exception:
		print('ERROR: Rabi_sweep_range  should be defined in the globals.h5 file called/managed by runmanger.')

	try:
		print(Rabi_sweep_power)
	except Exception:
		print('ERROR: Rabi_sweep_power  should be defined in the globals.h5 file called/managed by runmanger.')

	try:
		print(Rabi_sweep_resolution)
	except Exception:
		print('ERROR: Rabi_sweep_resolution  should be defined in the globals.h5 file called/managed by runmanger.')

	try:
		print(Rabi_sweep_duration)
	except Exception:
		print('ERROR: Rabi_sweep_duration  should be defined in the globals.h5 file called/managed by runmanger.')

	stop(t)
	print("Compiled test_globals!")
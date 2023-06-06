'''
	Defines python classes that group together sequence primitives for simplifying lab control/scripting.
'''
import builtins
from labscriptlib.ybclock.classes import *

def define_classes(name_space=globals(),_rf_larmor_detuning=0):
	''' Defines the objects for controlling our lasers '''

	#this the only way I found to actually define variables for use outside the module.
	builtins.blue 	= BlueLaser()
	builtins.green	= GreenLaser()
	builtins.red  	= RedLaser()


	#Non laser objects
	builtins.RF = RfRabiDrive(
		rabi_channel_ac 	= rabi_coil_field, 
		rabi_channel_dc 	= rabi_coil_dc_offset, 
		larmor_frequency	= rf_larmor_frequency+_rf_larmor_detuning)
	
	builtins.exp_cavity = ExperimentalCavity()

	#add some globals
	builtins.ms = 1e-3
	builtins.kHz = 1e3
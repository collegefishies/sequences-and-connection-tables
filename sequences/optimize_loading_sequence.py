'''
	Loads atoms from the Oven Up to the Optical Lattice, 
	applies the large bias field, and measures the "Vacuum" Rabi Splitting.
'''
from math import pi
import numpy as np
from labscript import start, stop, AnalogOut, DigitalOut,add_time_marker
from labscriptlib.ybclock.connection_table import define_connection_table
from labscriptlib.ybclock.subsequences import *
from labscriptlib.ybclock.subsequences.squeezing import squeezing_pulse_without_light_shift
from labscriptlib.ybclock.classes import define_classes


us = 1e-6; ms = 1e-3; kHz = 1e3

def main():

	#define prerequisites.
	define_connection_table(); define_classes(); HP8648Cfor759.constant(bridging_frequency_759);start()

	#load atoms to the optical lattice
	t = 10*us
	t += set_start_values(t)
	t += load_from_oven_to_optical_lattice(t,add_marker = False)
	t += wait(hold_atoms_after_loading)
	t += measure_and_prepare_atoms(t) #read unpolarized atom number.
	
	#Create a spin down state with a pi RF pulse
	t += RF.rabi_pulse(
				t        	= t,
				rabi_area	= pi + short_rabi_pi_pulse_correction,
				phase    	= 0,
				duration 	= 'min',
				samplerate  = 100*kHz
				)
	t += wait(10*ms)

	#measure Sz 
	measure_sz_x_times = 2
	for x in range(measure_sz_x_times):
		t += exp_cavity.scan(t, label='atoms_in_cavity', params={'unitary': RF.get_unitary()}) #measure Nup
		t += wait(5*ms)
		t += RF.rabi_pulse(
					t        	= t,
					rabi_area	= pi + short_rabi_pi_pulse_correction,
					phase    	= 0,
					duration 	= 'min',
					samplerate  = 100*kHz
					)
		t += wait(5*ms)
		t += exp_cavity.scan(t, label='atoms_in_cavity', params={'unitary': RF.get_unitary()}) #measure Ndown
		t += wait(5*ms)

	t += empty_then_measure_cavity_frequency(t)		
	t += take_background_green_mot_image(t)
	### Turn on mot again.
	t += mot_coil_current.ramp(t,
		duration=10*ms,
		initial=0,
		final=9.1,
		samplerate=10*kHz
		)
	set_end_values(t)
	#print the run duration
	print('Run duration: ' + str(t) + ' s')
	stop(t+0.02)

### take background mot image
def take_background_green_mot_image(t):
	ms = 1e-3

	trigger_duration = 20*ms
	green.mot.intensity.constant(t,value=LS_green_mot_loading_intensity)
	isometric_cam.expose(t,	name='green_mot', frametype='bg', trigger_duration=trigger_duration)

	return trigger_duration
if __name__ == '__main__':
	main()
	print("Compiled loading_sequence!")

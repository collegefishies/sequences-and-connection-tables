'''
	Loads atoms from the Oven Up to the Optical Lattice, 
	applies the large bias field, and measures the "Vacuum" Rabi Splitting.
'''
from math import pi
import numpy as np
from labscript import start, stop, AnalogOut, DigitalOut,add_time_marker
from labscriptlib.ybclock.connection_table import define_connection_table
from labscriptlib.ybclock.subsequences import *
from labscriptlib.ybclock.subsequences.squeezing import squeezing_pulse_without_light_shift, squeezing_pulse
from labscriptlib.ybclock.classes import define_classes

if __name__ == '__main__':

	us = 1e-6
	ms = 1e-3
	kHz = 1e3

	define_connection_table()
	define_classes()
	HP8648Cfor759.constant(bridging_frequency_759)

	# Begin issuing labscript primitives
	# start() elicits the commencement of the shot
	start()

	t = 10*us
	set_start_values(t)
	t += 100*ms


	t += load_from_oven_to_optical_lattice(t,add_marker = True)
	t += wait(hold_atoms_after_loading)
	#read unpolarized atom number.
	def measure_and_prepare_atoms(t,add_marker = False):
		t0 = t
		if not add_marker: add_time_marker(t, "Measure & Pump Atoms")
		add_time_marker(t, "Read Unpol. Atom #")
		#cavity scan #1
		t += exp_cavity.scan(t, params={'unitary': RF.get_unitary()}, label='atoms_in_cavity')
		t+= wait(50*ms)

		add_time_marker(t, "Polarize Atoms")
		
		t += spin_polarize_atoms(t,20*ms)
		RF.atom_unitary.prepare_atom_unitary(t)
		t+= wait(20*ms)

		#read atom number.
		#cavity scan #2
		t += exp_cavity.scan(t, params={'unitary': RF.get_unitary()}, label='atoms_in_cavity')
		return t-t0

	t += measure_and_prepare_atoms(t)
	
	#Create a CSS state through a pi/2 RF pulse
	tRFPiOver2 = t 
	t60HzPeriod = 16.6666*ms
	t += RF.rabi_pulse(
				t        	= t,
				rabi_area	= pi/2,
				phase    	= 0,
				duration 	= 'min',
				samplerate  = 100*kHz,
				detuning	= rf_larmor_detuning
				)
	t += wait(10*ms)


	# Squeezing: two pulses with pi RF pulse in the middle
	SQUEEZE = True
	COMPENSATE = False
	if SQUEEZE:
		if COMPENSATE:
			t += squeezing_pulse_without_light_shift(
				t,
				duration=squeezing_pulse_duration*ms,
				detuning_MHz=squeezing_detuning,
				squeezing_strength_V=squeezing_light_power,
				)
		else:
			t += squeezing_pulse(
				t,
				duration=squeezing_pulse_duration*ms,
				detuning_MHz=squeezing_detuning,
				squeezing_strength_V=squeezing_light_power,
				)
	else:
		t += 0.0252899

	t += wait(calibration_precession_time*ms)

	t += RF.rabi_pulse(
				t        	= t,
				rabi_area	= pi/2,
				phase    	= pi/2,
				duration 	= 4.5*ms,
				samplerate  = 100*kHz,
				detuning	= rf_larmor_detuning
				)
	t += wait(10*ms)


	#measure Sz 
	measure_sz_x_times = 2
	for x in range(measure_sz_x_times):
		t += exp_cavity.scan(t, label='atoms_in_cavity', params={'unitary': RF.get_unitary()}) #measure Nup
		t += wait(5*ms)
		t += RF.rabi_pulse(
					t        	= t,
					rabi_area	= pi,
					phase    	= 0,
					duration 	= 5.29*ms,
					samplerate  = 100*kHz
					)
		t += wait(5*ms)
		t += exp_cavity.scan(t, label='atoms_in_cavity', params={'unitary': RF.get_unitary()}) #measure Ndown
		t += wait(17*ms)


	t += wait(10*ms)
	# add_time_marker(t, "Empty then Scan")
	t += empty_then_measure_cavity_frequency(t)


	### take background mot image
	def take_background_green_mot_image(t):
		ms = 1e-3

		trigger_duration = 20*ms
		green.mot.intensity.constant(t,value=LS_green_mot_loading_intensity)
		isometric_cam.expose(t,	name='green_mot', frametype='bg', trigger_duration=trigger_duration)

		return trigger_duration
		
	t += take_background_green_mot_image(t)
	### Turn on mot again.
	t += mot_coil_current.ramp(t,
		duration=10*ms,
		initial=0,
		final=9.1,
		samplerate=10*kHz
		)
	set_end_values(t)

	# for ti in np.arange(100*ms,t, 1*ms):
	#	photon_counter_shutter.enable(ti)
	#	p7888_start_trigger.enable(ti)
	#	p7888_start_trigger.disable(ti+0.5*ms)
	#	pass
	# Stop the experiment shot with stop()
	stop(t+0.1)

print("Compiled loading_sequence!")

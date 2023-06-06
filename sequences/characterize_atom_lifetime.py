'''
	Loads atoms from the Oven Up to the Optical Lattice, 
	applies the large bias field, and measures the "Vacuum" Rabi Splitting.
'''
from math import pi

from labscript import start, stop, AnalogOut, DigitalOut,add_time_marker
from labscriptlib.ybclock.connection_table import define_connection_table
from labscriptlib.ybclock.subsequences import *
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


	#get atoms
	t += load_from_oven_to_optical_lattice(t,add_marker = True)
	#reduce atom number if desired	
	t += wait(hold_atoms_after_loading)
	#read unpolarized and polzarized atom number after loading
	def measure_and_prepare_atoms(t,add_marker = False):
		t0 = t
		if not add_marker: add_time_marker(t, "Measure & Pump Atoms")
		add_time_marker(t, "Read Unpol. Atom #")
		#cavity scan #1
		t += exp_cavity.scan(t, params={'unitary': RF.get_unitary()}, label='atoms_in_cavity')
		t+= wait(10*ms)

		add_time_marker(t, "Polarize Atoms")
		t += spin_polarize_atoms(t,20*ms)
		RF.atom_unitary.prepare_atom_unitary(t)
		t+= wait(20*ms)

		#read atom number.
		#cavity scan #2
		t += exp_cavity.scan(t, params={'unitary': RF.get_unitary()}, label='atoms_in_cavity')
		return t-t0

	t += measure_and_prepare_atoms(t)
	
	#measure Neta to see atom decay.
	# add_time_marker(t, "Scan Neta")
	#cavity scan #3
	for i in range(15):
		t += wait(10*ms)
		t += exp_cavity.scan(t, label='atoms_in_cavity', params={'unitary': RF.get_unitary()})
		t += wait(10*ms)

	t += wait(10*ms)
	#measure empty cavity frequency
	# add_time_marker(t, "Empty then Scan")
	t += empty_then_measure_cavity_frequency(t)


	### take background mot image for calculating SNR.
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
	# Stop the experiment shot with stop()
	stop(t+0.1)

print("Compiled loading_sequence!")

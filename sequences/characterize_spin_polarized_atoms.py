'''
	Loads atoms from the Oven Up to the Optical Lattice, 
	applies the large bias field, and measures the "Vacuum" Rabi Splitting.
'''
from math import pi

from labscript import start, stop, AnalogOut, DigitalOut,add_time_marker
from labscriptlib.ybclock.connection_table import define_connection_table
from labscriptlib.ybclock.subsequences import *
from labscriptlib.ybclock.classes import define_classes

def wait(duration):
	return duration

if __name__ == '__main__':

	ms = 1e-3
	kHz = 1e3

	define_connection_table()
	define_classes()
	HP8648Cfor759.constant(bridging_frequency_759)

	# Begin issuing labscript primitives
	# start() elicits the commencement of the shot
	start()

	set_default_values()

	t = 10.1*ms

	t += load_from_oven_to_optical_lattice(t,add_marker = False)

	t += ramp_magnetic_fields_for_cavity_readout(t)
	
	t += ramp_down_mot(t)

	t += wait(200*ms + 140*ms)

	#read unpolarized atom number.
	t += exp_cavity.scan(t, params={'unitary': RF.get_unitary()}, label='atoms_in_cavity')

	t+= wait(5*ms)

	t += spin_polarize_atoms(t)

	RF.atom_unitary.prepare_atom_unitary(t)

	t+= wait(20*ms)

	#read polarized atoms
	t += exp_cavity.scan(t, params={'unitary': RF.get_unitary()}, label='atoms_in_cavity')
	
	#cool atoms
	cooling_duration = 80*ms
	green.cooling.intensity.constant(t, value = 10)
	green.cooling.turnoff(t=t+cooling_duration)
	green.cooling.intensity.constant(t, value = 10)
	green.cooling.turnoff()


	#perform rabi pulse then cavity scan
	t += RF.rabi_pulse(
		t        	= t,
		rabi_area	= pi/2,
		phase    	= 0,
		duration 	= 2.29*ms,
		samplerate  = 100*kHz
		)

	t += wait(20*ms)

	t += exp_cavity.scan(t, label='atoms_in_cavity', params={'unitary': RF.get_unitary()})

	t += empty_then_measure_cavity_frequency(t)


	### Turn on mot again.
	t += mot_coil_current.ramp(t,
		duration=10*ms,
		initial=0,
		final=9.1,
		samplerate=10*kHz
		)
	set_default_values(t)
	# Stop the experiment shot with stop()
	stop(t+0.1)

print("Compiled loading_sequence!")

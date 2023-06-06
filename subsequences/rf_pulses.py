from math import pi
from labscriptlib.ybclock.subsequences import *

def nuclear_spin_ramsey_sequence(t, precession_time, samplerate, detuning=0, phase=0):
	''' Assumes spins are spin down and performs a ramsey sequence '''
	duration = 'min'
	t0 = t
	t += RF.rabi_pulse(
				t        	= t,
				rabi_area	= pi/2 + short_rabi_pulse_correction,
				phase    	= 0,
				duration 	= duration,
				samplerate  = samplerate,
				detuning	= 0
				)

	t += wait(precession_time)

	#detune the effective phase for larmor sequences without destroying the contrast.
	t += RF.rabi_pulse(
				t        	= t,
				rabi_area	= pi/2 + short_rabi_pulse_correction,
				phase    	= pi/2 + 2*pi*detuning*precession_time + phase,
				duration 	= duration,
				samplerate  = samplerate,
				detuning	= 0
				)
	return t - t0
	
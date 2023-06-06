from math import pi
from labscript import add_time_marker

def wait(x):
	return x
def return_next_60Hz_cycle(t, n=0):
	'returns duration til next (n+1)th clock cycle'
	from math import ceil
	N = ceil(t*60) + n #Hz
	dt = N/60 - t
	return dt

def squeezing_pulse(t,detuning_MHz, squeezing_strength_V,duration):
	'''
		#Components

		Two Light tones on the green, that componensates the ac light shift on
		the atomic spin. Assuming the cavity splitting is 4.5 MHz at Neta
		= 2000, we will apply two tones, one positive detuned 8 MHz from
		the atomic transition and one detuned -0.2 MHz? from the center

	'''
	if SQUEEZING:
		stretched_state_shift = f_atoms #frequency of the atoms relative to the probe at 160 MHz.
		# wcav_splitting = 4.5 MHz
		# detuned 8 MHz from the atomic transition == cavity transition
		green.probe.frequency.constant(t,value=stretched_state_shift+detuning_MHz,units="MHz")
		green.probe.intensity.constant(t, value=squeezing_strength_V)
		green.probe.turnoff(t+duration,warmup_value=0)
		
	exp_cavity.count_photons(t=t,duration=duration,label='squeezing_photons')
	return duration

def squeezing_pulse_without_light_shift(t, detuning_MHz,squeezing_strength_V,duration, add_marker=False):
	'''
		Two squeezing pulses with a Pi pulse in between to cancel the phase shift.
		This subsequence is synchronized with the 60 Hz cycles. It occurs in 4 cycles.
	'''
	#first squeezing light pulse to be introduce here
	t0 = t

	#quantize time to a 60 Hz clock cycle
	t += return_next_60Hz_cycle(t0)
	tsq = t
	if add_marker: add_time_marker(tsq, "SQWOLS: 0st 60Hz")
	#squeeze at the midpoint
	tpi = t0 + return_next_60Hz_cycle(t0, n=1)
	if add_marker: add_time_marker(tsq, "SQWOLS: 1st 60Hz")
	#set pi pulse for two cycles from now
	tsq2 = t0 + return_next_60Hz_cycle(t0, n=2)
	if add_marker: add_time_marker(tpi, "SQWOLS: 2st 60Hz")
	#squeeze at the other midpoint
	tf = t0 + return_next_60Hz_cycle(t0, n=3)
	if add_marker: add_time_marker(tsq2, "SQWOLS: 3st 60Hz")



	#squeeze centered at the clock cycle.
	dt = duration/2
	squeezing_pulse(tsq - dt/2, detuning_MHz=detuning_MHz, squeezing_strength_V=squeezing_strength_V, duration=dt)

	#pi pulse centered at the clock cycle
	dt = shortest_pi_pulse_time*(1 + short_rabi_pulse_correction/pi)
	if SQUEEZING_PI_PULSE:
		dt = RF.rabi_pulse(
						t        	= tpi - dt/2,
						rabi_area	= pi + short_rabi_pi_pulse_correction,
						phase    	= pi/2,
						duration 	= 'min',
						samplerate  = 100*kHz
					)

	#second squeezing light pulse at the 3 part of the cycle
	dt = duration/2
	squeezing_pulse(
		t = tsq2 - dt/2,
		detuning_MHz=detuning_MHz,
		squeezing_strength_V=squeezing_strength_V,
		duration=dt
	)

	return tf - t0
def squeezing_pulse_with_pi_pulse(t, detuning_MHz, squeezing_strength_V, duration,ramsey_phase):
	''' excite the atoms, squeeze, add pi phase shift, wait, then prepare for measurement '''
	t0 = t	
	#prepare the atoms with an excitation
	t += RF.rabi_pulse(
		t        	= t,
		rabi_area	= pi/2 + short_rabi_pulse_correction,
		phase    	= 0,
		duration 	= 'min',
		samplerate  = 100*kHz
	)
	#save the time that defines zero phase for the atoms 
	tPhase = t0
	#perform a squeezing pulse
	dt = squeezing_pulse(
		t,
		detuning_MHz=detuning_MHz,
		squeezing_strength_V=squeezing_strength_V,
		duration=duration
	)
	t += max(dt,10*ms)
	#perform a pi pulse in the center
	tPulse = t - tPhase
	t += RF.rabi_pulse(
		t        	= t,
		rabi_area	= pi,
		phase    	= pi/2,
		duration 	= 'min',
		samplerate  = 100*kHz
	)
	#wait for the same time as the pulse
	t += wait(tPulse)
	#perform final rotation for measurement
	t += RF.rabi_pulse(
		t        	= t,
		rabi_area	= pi/2,
		phase    	= ramsey_phase,
		duration 	= 'min',
		samplerate  = 100*kHz
	)
	return t - t0
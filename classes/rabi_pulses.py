'''
	#Mission

	To provide classes for providing simple control for the RfRabiDrive as
	well as keep track of the atom unitary via a spinor class. The
	RabiDrive classes should have a Spinor class contained within it.

	## Desired Usage
	```python
	rf = RabiDrive()
	clock = RabiDrive()

	rf.rabi_pulse(rabi_area,phase,duration,amplitude_correction)
	clock.rabi_pulse(...)
	```
'''

from math import pi, floor, ceil
import numpy as np
import scipy as sp
from numpy import cos, sin
import matplotlib.pyplot as plt
from math import floor

ms = 1e-3
us = 1e-6
kHz = 1e3

def round_duration(t,clock_samplerate=800*kHz, max_samplerate=100*kHz):
	t_in_clock_samples = floor(t*clock_samplerate)
class Spinor:
	'''

		This class keeps track of the *net* unitary applied to the atoms at the start of the experiment after preparation.

		The easiest way to keep track of the dark time is to use the just
		apply a unitary corresponding to free evolution during the dark
		time. During the rabi pulse, we transform to the RF rotating frame
		and then apply the stationary effective Hamiltonian. 


		interaction picture: \\(\\vec{\\psi'}  = \\hat{T} \\vec {\\psi} \\) 
		where \\(\\hat{T} = \\exp{\\frac{i}{\\hbar} \\omega_{RF}\\hat{\\sigma_z} (t - t')} \\) and
		\\(\\hat{H_0} = \\frac{\\hbar}{2} \\omega_L (\\hat{\\sigma_z}) \\) is the hamiltonian for the atoms in free space.

		The rotating frame interaction Hamiltonian is \\(\\hat{V}' = \\hat{T} \\hat{V} \\hat{T}^\\dagger\\). 
		Evidently, this outlines our transformation for Hermitian operators.

		#Piecewise Model

		Our atoms engage in piecewise evolution, either in the dark or interacting with a RF pulse.

	'''

	unitary     	= None #our net unitary operator
	t_last      	= None #time since last applied unitary 
	f_larmor    	= None #atomic precession frequency
	pauli_vector	= (
	            				np.matrix(
	            					[
	            						[0,	1],
	            						[1,	0]
	            					] #sx
	            				),
	            				np.matrix(
	            					[
	            						[0, 	-1j],
	            						[1j,	0]
	            					] #sy
	            				),
	            				np.matrix(
	            					[
	            						[1,	0],
	            						[0,	-1]
	            					] #sz,
	            				)
	)

	def __init__(self, f_larmor):
		self.f_larmor = f_larmor



	def prepare_atom_unitary(self, t):
		'''
			Set the spin unitary to the identity matrix and record the spin preperation time for keeping track of phase evolution.
		'''
		self.unitary = np.identity(2, dtype=complex)
		#save the preparation time.
		self.t_last = t

	def rabi_pulse(self, times, omegas, simulate=True):
		'''
			times, omegas are lists of all the times and rabi amplitudes of
			the drive. we use this to interpolate a function. make any
			arrays you define for your hamiltonian `np.array(
			[],dtype=complex)`! if you dont make it complex, your simulation will not evolve!
			this operator conserves probability by 99%.
		'''
		from scipy import interpolate
		from scipy import integrate
		if not simulate:
			print("Not Simulating Rabi Pulse...")
			unitary = np.empty((2,2,))
			unitary[:] = np.nan
			return unitary
		#check to see if pulses are sequential.
		t = times[0]
		duration = times[-1] - times[0]

		if (t - self.t_last) < 0:
			raise Exception("Rabi Pulses not applied in chronological order. Cannot simulate correctly.")


		#calculate spin precession since last unitary pulse.
		w = 2*pi*self.f_larmor
		U_free_space = sp.linalg.expm(
				-1j*w/2*(t-self.t_last)*self.pauli_vector[2]
			)

		#evolve atoms until just before we peform interaction.
		self.unitary = np.matmul(U_free_space, self.unitary)

		#evolve under rf_pulse
		#to figure out the Unitary need to figure out how up and down map.
		up = np.array([1,0],dtype=complex).reshape(-1)
		down = np.array([0,1], dtype=complex).reshape(-1)
		#define hamiltonian
		omega = interpolate.interp1d(times, omegas, fill_value=np.nan)
		# plt.plot(times, omegas)
		# plt.show()
		def H(t):
			H0 = 2*pi*self.f_larmor*np.array(self.pauli_vector[2],dtype=complex)/2
			H1 = omega(t)*np.array(self.pauli_vector[0], dtype=complex)/2
			return H0 + H1
		def derivative(t,psi):
			return np.matmul(-1j*H(t), psi)
		#set up solvers
		upSol = integrate.RK45(
			fun=derivative,
			t0=t,
			t_bound=times[-1],
			y0=up,
			rtol=1e-4
		)
		downSol = integrate.RK45(
			fun=derivative,
			t0=t,
			t_bound=times[-1],
			y0=down,
			rtol=1e-6
		)
		#solve
		print("\tSimulating Rabi Pulse...")
		while upSol.status == 'running':
			upSol.step()
		while downSol.status == 'running':
			downSol.step()
		#get final states to make unitary
		upF = upSol.y
		downF = downSol.y
		Urabi = np.outer(upF, np.conj(up)) + np.outer(downF, np.conj(down))
		# plt.plot(times, omegas, label='simulated rf')
		# plt.plot(times,1000* np.sin(times*2*pi*rf_larmor_frequency), label='LO')
		# plt.legend()
		# plt.show()
		if upSol.status == 'failed':
			assert "Error Rabi Pulse simulation failed. up part failed"

		if downSol.status == 'failed':
			assert "Error Rabi Pulse simulation failed. down part failed"
		self.unitary = np.matmul(Urabi,self.unitary)
		print(f"abs|U|^2 = {np.square(np.abs(self.unitary))}")
		psi = self.unitary @ down
		print(f"psi^2 = {np.square(np.abs(psi))}")

		self.t_last = t + duration
		return self.unitary



class RfRabiDrive:
	'''
		`atom_unitary` encodes the state of the spin via a unitary matrix.
	'''

	rabi_channel_ac 	= None
	rabi_channel_dc 	= None
	larmor_frequency	= None
	atom_unitary    	= None

	def __init__(self, rabi_channel_ac, rabi_channel_dc, larmor_frequency):
		'''
			`rabi_channel_ac` - Specify the analog channel for controlling the Rabi Field.
			`larmor_frequency` - Specify the precession frequency in Hertz.
		'''
		self.rabi_channel_dc 	= rabi_channel_dc
		self.rabi_channel_ac 	= rabi_channel_ac
		self.larmor_frequency	= larmor_frequency
		self.atom_unitary    	= Spinor(f_larmor=larmor_frequency)

	def round_time(self,t,dt=10*us):
		''' rounds time to nearest `dt` which is your resolution. '''
		Ntimes = floor(t/dt)
		return Ntimes*dt
	# def sin(t, duration, amplitude, angfreq, phase, dc_offset, samplerate):
	#	transition_times = np.arange(t, t+duration, 1/samplerate)
	#	for each_t in transition_times:
	#		self.rabi_channel_ac.
	#	pass
	def rabi_pulse(self,t,phase,rabi_area=None,rabi_freq=None,duration=None,samplerate=100e3,amplitude_correction=0,detuning=0, simulate=True):
		'''
			`rabi_area`           	- the rotated angle of the spin state in radians.
			`phase`               	- the phase of the Rabi Drive relative to the Local Oscillator (LO) or Oscillation Phase of the atoms.
			`duration`            	- how long should the pulse be applied for, can also be 'min' to minimize duration.
			`amplitude_correction`	- fractional correction one should apply to the amplitude to accomodate for digitization errors.
		'''
		t0 = t
		# t = self.round_time(t,dt = 1/samplerate)

		sine_area_correction = 1
		rf_angfreq = 2*pi*self.larmor_frequency + 2*pi*detuning

		if duration is not None and rabi_freq is None:
			#calculate rabi_amplitude
			if duration == 'min' and rabi_area == 'max':
				raise "Error, duration and rabi_area cannot both be extremized simultaneously"
		
			if rabi_area == 'max':
				rabi_amplitude = max_rabi_amplitude-1e-9
				rabi_area = rabi_amplitude*duration/pi_pulse_area*pi
			
			if duration == 'min':
				rabi_amplitude = max_rabi_amplitude-1e-9
				duration = pi_pulse_area/rabi_amplitude*(rabi_area/pi)
			else:
				#pi_pulse_area has no factors of pi in the formula
				#pi_pulse_area = V*T/2 (no pi's)
				#where T is the rabi flopping period
				rabi_amplitude = (1 + amplitude_correction)*pi_pulse_area/pi * rabi_area/duration * sine_area_correction
		elif rabi_freq is not None:
			#calculate the max rabi_amp
			max_rabi_frequency	= rf_rabi_frequency #global var
			rabi_amplitude    	= (max_rabi_amplitude - 1e-9) * (rabi_freq/max_rabi_frequency)
			if duration is None:
				duration	= rabi_area/rabi_amplitude * pi_pulse_area/pi
			elif rabi_area is None:
				rabi_area   = rabi_area = rabi_amplitude*duration/pi_pulse_area*pi
			else:
				raise "Error: Either rabi_area or duration needs to be specified."
		else:
			raise "Error: Neither rabi_freq nor duration was specified or both were specified."



		#perform theoretical rabi pulse
		times = np.arange(t,t+duration, 1/10/samplerate)
		self.atom_unitary.rabi_pulse(
			times 	= times,
			omegas	= 2*rabi_area/duration*sin(rf_angfreq*times + phase),
			simulate = simulate,
		)

		#perform actual rabi pulse
		self.rabi_channel_dc.constant(t,value=dc_offset)


		if rabi_amplitude > max_rabi_amplitude:
			raise Exception(f"Error: You're trying to set the rabi_amplitude {rabi_amplitude} larger than the largest linear value {max_rabi_amplitude}.")
		t += self.rabi_channel_ac.sine(
			t         	= t,
			duration  	= duration,
			amplitude 	= rabi_amplitude,
			angfreq   	= rf_angfreq,
			phase     	= phase + rf_angfreq*t, #the simulations match actual rf curves with this second term in place.
			dc_offset 	= 0,
			samplerate	= samplerate
		)

		self.rabi_channel_ac.constant(t,value=0)
		self.rabi_channel_dc.constant(t,value=0)

		return t - t0

	def get_unitary(self):
		'''
			returns atomic state for analysis.
		'''
		return self.atom_unitary.unitary


if __name__ == '__main__':
	RfRabiDrive()

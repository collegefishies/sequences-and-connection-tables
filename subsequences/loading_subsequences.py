'''
	Holds sequences regarding loading atoms into our traps.

	All functions return their duration.

	#An Outline of How MOT Trapping Works

	Let's start from what we know a MOT should do. It should cool and it should
	trap. From the fact that it should cool, and we presume it cools via simple
	Doppler cooling, we can surmise that all MOT beams must be red detuned.

	From the fact it should trap, we can surmise that we need to create a
	position dependent force. I leave it as an exercise to the reader, to show
	that a position dependent energy of the excited state can give this position
	dependent force.

	One of the easiest ways we perform this position dependent force is via a
	magnetic field gradient and the magnetic properties of angular momentum
	excited states. The magnetic field gradient pushes the atoms into resonance
	at certain positions causing them to get forced into the center of the trap.

	#A summary of MOT characteristics

	By analysis of the above properties, we can determine, that the trap size is
	a function of magnetic field gradient and detuning, and the cooling is a
	function of the detuning.

	We can also surmise that the MOT trapping position depends on the
	`bias_field`. 

'''

from labscript import add_time_marker
from .mloop_utils import simple_mloop_ramp

def wait(duration):
	return duration

def blue_mot(t,duration,add_marker=False,take_picture=False, bg_picture=False):
	'''
	# Blue MOT Loading Sequence

	It's very simple simple turn on all the lights and magnetic fields, and let 
	the atoms trap.

	The Blue MOT is assisted by Green Molasses (Doppler Cooling).
	'''

	#turn on the blue mot
	us = 1e-6
	ms = 1e-3
	if add_marker: add_time_marker(t, "LS: Blue MOT", verbose=True)
	#set bicolor mot frequency for green
	# set trigger time of FPGA_DDS9
	# FPGA_DDS9.triggerSet(10*us)
	# green_frequency_fpga_trigger.enable(10*us)
	# set initial value of the DDS
	# FPGA_DDS9.constant(
	#	t=t,
	#	channel=int(0b0001),
	#	value = ('freq',LS_bicolor_mot_frequency_for_green,'MHz'),
	#	description='initial value'
	#	)
	# FPGA_DDS9.constant(
	#	t=t+10*us,
	#	channel=int(0b0001),
	#	value=('ampl', 0.5, '1'),
	#	description='initial value'
	#	)

	#turn off extra light sources that can interrupt loading
	green.cooling_pi.turnoff(t,warmup_value=10)

	#set voltage limit on mot
	mot_coil_voltage.constant(t,value=8.5)

	#set magnetic fields
	mot_coil_current.constant(t, value=9.1)
	x_bias_field.constant(t, value=-0.608)
	y_bias_field.constant(t, value=1.374)
	z_bias_field.constant(t, value=2.2)

	#set light power
	blue.mot.intensity.constant(t, value=LS_blue_mot_intensity)
	green.mot.intensity.constant(t, value=LS_green_mot_intensity) #why? Two Color Mot thats why.
	#the green light serves as extra doppler cooling.


	if take_picture:
		ms = 1e-3
		trigger_duration = 20*ms
		if t + duration- trigger_duration < 0:
			#we're giving no time for the mot to load, so 
			#just set the duration to the trigger_duration
			duration = trigger_duration


		#take background picture
		if bg_picture:
			print("Warning: BG Picture is not implemented yet.")

		# 	wide_angle_cam.expose(t,
		# 		name            	='blue_mot', 
		# 		frametype       	='bg',
		# 		trigger_duration	=trigger_duration
		# 	)

		# take picture with atoms
		wide_angle_cam.expose(t+duration-trigger_duration,
			name            	='blue_mot',
			frametype       	='atoms',
			trigger_duration	=trigger_duration
		)

		#set duration to be the larger of the two duration, trigger_duration
		duration = max(duration,trigger_duration)

	return duration

def transfer_blue_mot_to_green_mot(t,duration, samplerate,add_marker=False,take_picture=False):
	'''Ramp down blue light while moving atoms to green MOT position.'''
	if add_marker: add_time_marker(t, "LS: Transfer Blue MOT", verbose=True)
	#ramp down blue
	blue.mot.intensity.ramp(t, duration, initial=LS_blue_mot_intensity, final=0.05, samplerate=samplerate)
	#turn off the blue light at end of ramp
	blue.mot.intensity.turnoff(t+duration, warmup_value=0.28)
	
	#move magnetic field zero
	x_bias_field.ramp(t, duration, initial=-0.608,	final=1.6,  	samplerate=samplerate)
	y_bias_field.ramp(t, duration, initial=1.374, 	final=-0.19,	samplerate=samplerate)
	z_bias_field.ramp(t, duration, initial=2.2,   	final=0,    	samplerate=samplerate)


	
	return duration

def transfer_to_triplet_mot(t,freq_ramp_duration,intensity_ramp_duration,hold_time,samplerate, add_marker=False,take_picture=True):
	'''ramp the green mot frequency closer to resonance. 

		The frequency ramp and intensity ramp are currently sequential, there is no offset.'''
	if add_marker: add_time_marker(t, "LS: Transfer to Triplet MOT", verbose=True)
	
	# ramp frequency from 'bicolor_mot_frequency_for_green' to 'green_mot_frequency'
	t += FPGA_DDS9.ramp(
		t=t,
		duration=freq_ramp_duration,
		channel=int(0b0001),
		initial_value=('freq', LS_bicolor_mot_frequency_for_green, 'MHz'),
		final_value=('freq', green_mot_frequency, 'MHz'),
		number_of_steps=2000,
		description='end ramp'
		)

	# take picture for far green MOT
	if take_picture:
		ms = 1e-3
		trigger_duration = 20*ms

		wide_angle_cam.expose(t,
			name            	='green_mot_far',
			frametype       	='atoms',
			trigger_duration	=trigger_duration
		)
		t+= trigger_duration

	#
	# Add the PTS time markers for the green fpga trigger.(LEGACY CODE)
	#
	#		record timestamps for when we shift frequencies of the green using the PTS
	# tPTS = t; #577ms in Excel Sequences
	# add_time_marker(tPTS, "PTS: 1st to 2nd")
	# tPTS += 240*ms; 
	# add_time_marker(tPTS, "PTS: 2nd to 3rd")
	# tPTS += 20*ms;
	# add_time_marker(tPTS, "PTS: 3rd to 4th")

	#Ramp intensity for reducing atom scattering
	#ramp down green power so we don't blind the camera.
	t += green.mot.intensity.ramp(t, duration=intensity_ramp_duration, initial=LS_green_mot_intensity, final=LS_green_mot_loading_intensity, samplerate=samplerate)



	#hold the conditions for a little while
	return freq_ramp_duration+intensity_ramp_duration+hold_time
	
def position_atoms_to_optical_lattice(t, duration,samplerate, add_marker=False):
	#move the MOT center again
	if add_marker: add_time_marker(t, "LS: Move to Opt. Latt.", verbose=True)
	x_bias_field.ramp(t, duration, initial=1.6,  	final=x_bias_field_loading,	samplerate=samplerate)
	y_bias_field.ramp(t, duration, initial=-0.19,	final=y_bias_field_loading,	samplerate=samplerate)
	z_bias_field.ramp(t, duration, initial=0,    	final=z_bias_field_loading,	samplerate=samplerate)

	return duration

def mloop_position_atoms_to_optical_lattice(t, duration,samplerate, add_marker=False):
	#move the MOT center again
	if add_marker: add_time_marker(t, "LS:ML: Move to Opt. Latt.", verbose=True)
	simple_mloop_ramp(
		parameter=x_bias_field,
		param_name='TRANSFER_x_bias_field',
		t=t,
		duration=duration,
		initial=1.6,
		final=x_bias_field_loading,
		samplerate=samplerate
	)
	simple_mloop_ramp(
		parameter=y_bias_field,
		param_name='TRANSFER_y_bias_field',
		t=t,
		duration=duration,
		initial=-0.19,
		final=y_bias_field_loading,
		samplerate=samplerate
	)
	simple_mloop_ramp(
		parameter=z_bias_field,
		param_name='TRANSFER_z_bias_field',
		t=t,
		duration=duration,
		initial=0,
		final=z_bias_field_loading,
		samplerate=samplerate
	)                                          
	# x_bias_field.ramp(t, duration, initial=1.3,  	final=x_bias_field_loading,	samplerate=samplerate)
	# y_bias_field.ramp(t, duration, initial=-0.15,	final=y_bias_field_loading,	samplerate=samplerate)
	# z_bias_field.ramp(t, duration, initial=0,    	final=z_bias_field_loading,	samplerate=samplerate)

	return duration

def optimize_position_atoms_to_optical_lattice(t, duration,samplerate, add_marker=False):
	'''
		The sequence to use when we're using MLOOP to optimize the atom loading. Its empty for now.
	'''
	pass

def hold_atoms(t, duration,add_marker=False):
	if add_marker: add_time_marker(t, "LS:Hold Green MOT", verbose=True)
	return duration

def lattice_loading(t, take_picture,add_marker=False, take_picture_DEBUG=False):
	t0 = t
	t += position_atoms_to_optical_lattice(t,	duration= 40*ms,	samplerate=1*kHz, add_marker=add_marker)

	#take a picture of the atoms
	if add_marker: add_time_marker(t, "LS: Green MOT Picture", verbose=True)
	if take_picture:
		isometric_cam.expose(t,	name='green_mot', frametype='almost_loaded', trigger_duration=20*ms)
	if take_picture_DEBUG:
		#allows one to take a picture of the mot while it's moving.
		#this lets us get a bright TRACE of it's path.
		isometric_cam.expose(t0+25*ms,	name='green_mot', frametype='trace', trigger_duration=2*ms)

	t += hold_atoms(t,	duration= 40*ms,add_marker=add_marker)

	if add_marker: add_time_marker(t, "LS: Last Stage Cooling")
	FPGA_DDS9.constant(
		t,
		channel=int(0b0001),
		value=('freq',lattice_loading_frequency,'MHz'),
		description='last stage cooling during loading'
		)
	t += 60*ms #E.M. Add 60 ms load to see if it fixes loading issues
	return t - t0 

def mloop_lattice_loading(t, take_picture,add_marker=False):
	t0 = t
	t += mloop_position_atoms_to_optical_lattice(t,	duration= 40*ms,	samplerate=1*kHz, add_marker=add_marker)

	#take a picture of the atoms
	if add_marker: add_time_marker(t, "LS: Green MOT Picture", verbose=True)
	if take_picture:
		isometric_cam.expose(t,	name='green_mot', frametype='almost_loaded', trigger_duration=20*ms)

	t += hold_atoms(t,	duration= 40*ms,add_marker=add_marker)

	if add_marker: add_time_marker(t, "LS: Last Stage Cooling")
	FPGA_DDS9.constant(
		t,
		channel=int(0b0001),
		value=('freq',lattice_loading_frequency,'MHz'),
		description='last stage cooling during loading'
		)
	t += 60*ms #E.M. Add 60 ms load to see if it fixes loading issues
	return t - t0 

def ramp_magnetic_fields_for_cavity_readout(t, add_marker = True):

	#ramp magnetic fields (for setting atoms on resonance with cavity)
	if add_marker: add_time_marker(t, "LS: Ramp Bias Fields.")
	ramp_duration = 30*ms
	z_bias_field.ramp(t, duration=ramp_duration, initial=z_bias_field_loading,final=spin_b_field_z,samplerate=10*kHz)
	y_bias_field.ramp(t, duration=ramp_duration, initial=y_bias_field_loading,final=y_bias_field_in_cavity,samplerate=10*kHz)
	x_bias_field.ramp(t, duration=ramp_duration, initial=x_bias_field_loading,final=x_bias_field_in_cavity,samplerate=10*kHz)
	return ramp_duration

def ramp_down_mot(t, add_marker=False):

	t0 = t
	us = 1e-6
	if add_marker: add_time_marker(t, "LS: Ramp MOT Field")
	#change green frequency and turn off mot light
	green.mot.turnoff(t,warmup_value=0.3)
	FPGA_DDS9.constant(t+10*us,
		channel=int(0b0001),
		value=('freq', green_laser_frequency, 'MHz'),
		description='working green frequency'
	)
	#ramp down mot
	t+= mot_coil_current.ramp(t,
		duration=20*ms,
		initial=9.1,
		final=9.1*(8/8.5),
		samplerate= 10*kHz
	)

	t+= mot_coil_current.ramp(t,
		duration=40*ms,
		initial=9.1*(8/8.5),
		final=9.1*(8/8.5)*0.8,
		samplerate=10*kHz
		)

	t+= mot_coil_current.ramp(t,
		duration=50*ms,
		initial=9.1*(8/8.5)*0.8,
		final=9.1*(8/8.5)*0.8/4,
		samplerate=10*kHz
	)

	t+= mot_coil_current.ramp(t,
		duration=35*ms,
		initial=9.1*(8/8.5)*0.8/4,
		final=0,
		samplerate=10*kHz
	)

	return t-t0

def load_from_oven_to_optical_lattice(t, add_marker=False, take_picture=True):
	'''  This is meta-subsequence. It holds all the calls for loading from the
	oven up until loading into the optical lattice.'''
	if not add_marker: add_time_marker(t, "Loading Sequence")
	ms = 1e-3
	kHz = 1e3

	t0 = t
	#load the atoms
	t += blue_mot(t,                      	duration= LS_blue_mot_duration,	take_picture=take_picture, add_marker=add_marker)
	t += transfer_blue_mot_to_green_mot(t,	duration= 40*ms,               	samplerate=1*kHz, add_marker=add_marker)
	
	t += transfer_to_triplet_mot(t,
		freq_ramp_duration= 80*ms,
		intensity_ramp_duration=40*ms,
		hold_time=0*ms,
		samplerate=1*kHz, add_marker=add_marker)

	t += lattice_loading(t, take_picture=take_picture, add_marker=add_marker, take_picture_DEBUG=take_picture_of_moving_mot)

	t += ramp_magnetic_fields_for_cavity_readout(t, add_marker=add_marker)
	t += ramp_down_mot(t, add_marker=add_marker)

	t += wait(200*ms + 140*ms)

	return t-t0

def mloop_load_from_oven_to_optical_lattice(t, add_marker=False, take_picture=True):
	'''  This is meta-subsequence. It holds all the calls for loading from the
	oven up until loading into the optical lattice.'''
	if not add_marker: add_time_marker(t, "Loading Sequence")
	ms = 1e-3
	kHz = 1e3

	t0 = t
	#load the atoms
	t += mloop_blue_mot(t,                	duration= LS_blue_mot_duration,	take_picture=take_picture, add_marker=add_marker)
	t += transfer_blue_mot_to_green_mot(t,	duration= 40*ms,               	samplerate=1*kHz, add_marker=add_marker)
	
	t += transfer_to_triplet_mot(t,
		freq_ramp_duration= 80*ms,
		intensity_ramp_duration=40*ms,
		hold_time=0*ms,
		samplerate=1*kHz, add_marker=add_marker)

	t += mloop_lattice_loading(t, take_picture=take_picture, add_marker=add_marker)

	t += ramp_magnetic_fields_for_cavity_readout(t, add_marker=add_marker)
	t += ramp_down_mot(t, add_marker=add_marker)

	t += wait(200*ms + 140*ms)

	return t-t0

def spin_polarize_atoms(t,duration):
	'''
		Polarize atoms and count the number of pump photons.
	'''
	t0 = t
	#pump atoms
	pump_duration = duration
	#set green frequency for the spin polarization
	FPGA_DDS9.constant(
		t=t,
		channel=(0b0001),
		value=('freq', spin_polarization_frequency, 'MHz'),
		description='spin_polarization'
		)
	green.pump.intensity.constant(t, value=spin_polarization_power, overload=True)
	#add counting duration buffer to prevent photons from leaking through to the cavity scans in the analysis
	exp_cavity.count_photons(t=t,duration=pump_duration+10*ms,label='pump_photons')
	t+= pump_duration
	green.pump.turnoff(t,warmup_value=0, overload=True)
	#set the frequency back to the old value.
	FPGA_DDS9.constant(
		t=t,
		channel=(0b0001),
		value=('freq', green_laser_frequency, 'MHz'),
		description='working_green_frequency'
		)


	#wait for the shutter to close
	t+= +10*ms

	return t-t0

def empty_then_measure_cavity_frequency(t):
	t0 = t
	#perform an empty cavity scan
	blue.mot.intensity.constant(t, value=0.28)
	t += 20*ms
	blue.mot.intensity.turnoff(t,warmup_value=0.28)
	t += exp_cavity.scan(t, label='empty_cavity')

	return t-t0

def measure_and_prepare_atoms(t,add_marker = False):
	t0 = t
	if not add_marker: add_time_marker(t, "Measure & Pump Atoms")
	if add_marker: add_time_marker(t, "Read Unpol. Atom #")
	#cavity scan #1
	t += exp_cavity.scan(t, params={'unitary': RF.get_unitary()}, label='atoms_in_cavity')
	t += wait(5*ms)

	if POLARIZE_ATOMS:
		if add_marker: add_time_marker(t, "Polarize Atoms")
		t += spin_polarize_atoms(t,spin_polarization_duration*ms)
	else:
		t += wait(spin_polarization_duration*ms)
	RF.atom_unitary.prepare_atom_unitary(t)
	t+= wait(5*ms)

	#read atom number.
	#cavity scan #2
	if add_marker: add_time_marker(t, "First Cavity Scan")
	t += exp_cavity.scan(t, params={'unitary': RF.get_unitary()}, label='atoms_in_cavity')
	return t-t0

print("Imported 'loading_subsequences'")
from labscript import add_time_marker

def wait(x):
	return x
ms = 1e-3
def set_start_values(t=5e-6, execution_number=0, add_marker=False):
	'''
		Run this at the beginning of the sequence.

		This sets all the default values of the experiment to prep the machine.
		Execution_number allows one to only set a value once, if it's only being used once at the very start of the experiment.

	'''
	t0 = t
	us = 1e-6 
	if add_marker: add_time_marker(t, "Set Start Values")

	#FPGA
	if execution_number == 0:
		FPGA_DDS9.triggerSet(t+10*us)
		green_frequency_fpga_trigger.enable(t+10*us) 
		
	FPGA_DDS9.constant(
		t=t+20*us,
		channel=(0b0001),
		value=('freq', LS_bicolor_mot_frequency_for_green, 'MHz'),
		description='initial value'
		)
	FPGA_DDS9.constant(
		t=t+30*us,
		channel=0b0001,
		value=('ampl',0.5,'1'),
		description='initial value'
		)

	t += wait(15*ms)
	t += set_end_values(t ,execution_number=0, add_marker=add_marker)
	
	return t - t0

def set_end_values(t=5e-6, execution_number=1, add_marker=False):
	'''
		Run this at the end of the sequence.

		This sets all the values of the experiment to be ready for the next shot.

	'''
	t0 = t
	us = 1e-6 
	if add_marker: add_time_marker(t, "Set Start Values")
	#set up oven
	oven_current_control.constant(t, value=oven_current)

	#set up mot fields
	mot_coil_voltage.constant(t,value=8.5)
	mot_coil_current.constant(t, value=9.1)

	#set up bias fields
	x_bias_field.constant(t, value=-0.608)
	y_bias_field.constant(t, value=1.374)
	z_bias_field.constant(t, value=2.2)

	#set up red laser
	red.cavity.intensity.turnon(t, value=red_trap_power_default, overload=True)

	#set up blue laser
	blue.mot.intensity.constant(t,value=LS_blue_mot_intensity, overload=True)

	#set up green laser
	#mot
	green.mot.intensity.constant(t,value=LS_green_mot_intensity, overload=True)

	#probe
	green.probe.turnoff(t, warmup_value=0, overload=True)
	probe_shutter.enable(t)
	#frequency
	if (execution_number == 1):
		green_frequency_fpga_trigger.disable(t)


	#cooling
	green.cooling_pi.turnoff(t, warmup_value=10.0, overload=True)
	green.cooling_sigma.turnoff(t, warmup_value=0, overload=True)

	#photon counter
	photon_counter_shutter.enable(t)

	return t - t0
'''

This is a set of functions to be used with the `mloop_config_XXXX.py` scripts
stored in `ybclock/scripts/mloop`. That script programatically generates
parameters to loop over, this set of functions programatically uses them.

'''
import json
def number_of_mloop_vars(key=None):
	'''	Converts the global variable 'mloop_vars_tuple' to a dictionary and returns the value, which is the number of parameters under that name.
	'''
	mloop_vars_dictionary = json.loads(mloop_vars_dict)

	if key:
		return mloop_vars_dictionary[key]
	else:
		return mloop_vars_dictionary

def return_mloop_vars(param_name):
	'''
		Returns a list of values for the variables defined by 'param_name' stored in the MLOOP globals group.
	'''
	var_list = []

	# try:
	# except Exception as e:
	#	print(f"Failed to get amount of parameters: {e}")
	number = int(number_of_mloop_vars(param_name))
	print(number)

	for i in range(number):
		var_list.append(eval(f"{param_name}{i:02d}"))

	return var_list

def simple_mloop_ramp(t, duration, parameter, initial,samplerate, final=None,param_name=None,parameter_list=None):
	'''
		Creates a continuous piecewise linear ramp given the parameter_list with evenly spaced points.

		Vars:

			t             	- initial time of ramp
			duration      	- duration of ramp
			parameter     	- the labscript variable/controller (AnalogOutput) that has ramp and constant functionality.
			parameter_list	- a list of numbers that defines the height of the piecewise linear ramp.
			param_name    	- a string that return_mloop_vars
			initial, final	- values you want the ramp to take at the boundaries
	'''

	if param_name is not None:
		parameter_list = return_mloop_vars(param_name)

	#add in the initial and final points
	if initial is not None:
		parameter_list.insert(0,initial)
	if final is not None:
		parameter_list.append(final)


	nramps = len(parameter_list)-1
	dt = duration/nramps
	for i in range(nramps):
		parameter.ramp(
			t=t,
			duration=dt,
			initial=parameter_list[i],
			final=parameter_list[i+1],
			samplerate=samplerate
		)
		t += dt
	return duration

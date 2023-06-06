''' 
	
	This script runs an MLOOP sequence to load atoms into the cavity when it's drifted away, assumes the green mot is visible.

'''
try:
	from mloop_lib import *
except:
	pass
try:
	from .mloop_lib import *
except:
	pass

if __name__ == "__main__":

	#parameters to optimize
	input_params = {
		"lattice_loading_frequency":	{"min":49.5, "max": 51.5, "start":50.22, "multiple":False, "num_parameters":1},
		"green_mot_frequency":	{"min":49.5, "max": 51.5, "start":50.22, "multiple":False, "num_parameters":1},
		"y_bias_field_loading":     	{"min":-0.4, "max": 0.4, "start":-0.12, "multiple":False, "num_parameters":1},
		"z_bias_field_loading":     	{"min":-0.6, "max": 0.9, "start":0.16, "multiple":False, "num_parameters":1},
	}

	#update initial values of parameters with last known working values
	input_params  = update_start_values(initial_globals_file, input_params)

	
	#create the mloop config file
	output = create(input_params)

	# print out the in use parameters
	print(output['param_names'])
	print(output['first_params'])

	# update the globals file to have the new mloop vars
	update_globals()
	# update_drifting_variables()
	repack_globals(initial_globals_file)
	repack_globals(globals_file)
	#get group names of parameters that already exist in globals file.
	groupnames_of_input_params = get_groupnames(initial_globals_file, input_params)
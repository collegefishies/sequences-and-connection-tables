
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
		"green_mot_frequency":               	{"min":49, "max": 50.9, "start":50.4, "multiple":False, "num_parameters":1},
		"lattice_loading_frequency":         	{"min":49, "max": 50.9, "start":50.22, "multiple":False, "num_parameters":1},
		"y_bias_field_loading":              	{"min":-1, "max": 1, "start":-0.12, "multiple":False, "num_parameters":1},
		"z_bias_field_loading":              	{"min":-1.5, "max": -0.5, "start":0.16, "multiple":False, "num_parameters":1},
		"LS_bicolor_mot_frequency_for_green":	{"min":42, "max": 50, "start":47, "multiple":False, "num_parameters":1},
		"LS_blue_mot_intensity":             	{"min":0.28, "max": 0.39, "start":0.3, "multiple":False, "num_parameters":1},
		"LS_green_mot_loading_intensity":    	{"min":0.09, "max": 0.3, "start":0.12, "multiple":False, "num_parameters":1},
		"LS_green_mot_intensity":            	{"min":0, "max": 0.4, "start":0.3, "multiple":False, "num_parameters":1},
		"spin_polarization_frequency":       	{"min":48, "max": 51, "start":49, "multiple":False, "num_parameters":1},
		"spin_polarization_power":           	{"min":0, "max": 6, "start":1, "multiple":False, "num_parameters":1},
		# "exp_cavity_scan_power":           	{"min":1.2, "max": 1.3, "start":1, "multiple":False, "num_parameters":1},
	}

	#update initial values of parameters with last known working values
	input_params  = update_start_values(initial_globals_file, input_params)
	input_params  = update_start_values(cavity_scan_globals_file, input_params)

	
	#create the mloop config file
	max_num_runs = get_runs_from_time(h=12)
	max_num_runs_without_better_params = get_runs_from_time(h=10)

	output = create(
		input_params,
		learner='neural_net',
		max_num_runs=max_num_runs,
		max_num_runs_without_better_params=max_num_runs_without_better_params
	)

	# print out the in use parameters
	print(output['param_names'])
	print(output['first_params'])

	# update the globals file to have the new mloop vars
	update_globals(input_params=input_params,config_dict=output)
	# update_drifting_variables()
	repack_globals(initial_globals_file)
	repack_globals(globals_file)
	#get group names of parameters that already exist in globals file.
	groupnames_of_input_params = get_groupnames(initial_globals_file, input_params)
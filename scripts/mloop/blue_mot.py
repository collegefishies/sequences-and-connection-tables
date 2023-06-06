

try:
	from mloop_lib import *
except:
	pass
try:
	from .mloop_lib import *
except:
	pass


if __name__ == "__main__":

	input_params = {
		# "LS_bicolor_mot_frequency_for_green":	{"min":40, "max": 50, "start":47, "multiple":False, "num_parameters":1},
		# "LS_blue_mot_intensity":             	{"min":0.28, "max": 0.4, "start":0.3, "multiple":False, "num_parameters":1},
		"green_mot_frequency":           	{"min":50.3, "max": 50.65, "start":50.48, "multiple":False, "num_parameters":1},
		"lattice_loading_frequency":           	{"min":50.1, "max": 50.65, "start":50.32, "multiple":False, "num_parameters":1},
		"x_bias_field_loading":                	{"min":5.0, "max": 5.3, "start":5.1, "multiple":False, "num_parameters":1},
		"y_bias_field_loading":                	{"min":-1, "max": 1, "start":0.5, "multiple":False, "num_parameters":1},
		"z_bias_field_loading":                	{"min":-1.5, "max": 1, "start":-0.8, "multiple":False, "num_parameters":1},
		"x_bias_field_loading_in_cavity":      	{"min":-1.5, "max": 1, "start":-0.02, "multiple":False, "num_parameters":1},
		"y_bias_field_loading_in_cavity":      	{"min":-2.5, "max": 1, "start":-1.86, "multiple":False, "num_parameters":1},
	}




	output = create(input_params)

	#print out the in use parameters
	print(output['param_names'])
	print(output['first_params'])

	#deletes old variables if generated.
	delete_MLOOP_globals("MLOOP")
	delete_MLOOP_globals("MLOOP_VARS")

	#creates the globals in the MLOOP folder if they dont already exist.
	create_globals(output['param_names'],output['first_params'])

	#save mloop_vars_tuple
	mloop_vars_tuple = []
	for key in input_params:
		mloop_vars_tuple.append(tuple((key, input_params[key]["num_parameters"])))
	mloop_vars_tuple = tuple(mloop_vars_tuple)
	create_global('mloop_vars_tuple',str(mloop_vars_tuple),'MLOOP_VARS') #you need the str() so it doesn't store as a list of lists.
	
	repack_globals()
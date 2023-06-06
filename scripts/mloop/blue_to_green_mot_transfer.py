''' 
	
	This script is for optimizing the Blue To Green MOT Transfer
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

	input_params = {
		"TRANSFER_x_bias_field":{"min":-1.5, "max": 5.7, "start": 1.3, "end": 5.29, "multiple":True, "num_parameters":3},
		"TRANSFER_y_bias_field":{"min":-.5, "max": 0.8, "start": -0.15, "end": 0.32, "multiple":True, "num_parameters":3},
		"TRANSFER_z_bias_field":{"min":-1, "max": 1, "start": 0, "end": -0.80, "multiple":True, "num_parameters":3},
		"TRANSFER_green_frequency":{"min":40, "max": 50, "start": 43.5, "end": -0.80, "multiple":False, "num_parameters":1},
	}




	output = create(input_params)

	print(output['param_names'])
	print(output['first_params'])
	delete_MLOOP_globals("MLOOP")
	delete_MLOOP_globals("MLOOP_VARS")
	create_globals(output['param_names'],output['first_params'])

	#save mloop_vars_tuple
	mloop_vars_tuple = []
	for key in input_params:
		mloop_vars_tuple.append(tuple((key, input_params[key]["num_parameters"])))
	mloop_vars_tuple = tuple(mloop_vars_tuple)
	create_global('mloop_vars_tuple',str(mloop_vars_tuple),'MLOOP_VARS') #you need the str() so it doesn't store as a list of lists.
	
	repack_globals()
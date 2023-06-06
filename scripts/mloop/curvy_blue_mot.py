''' 
	#Curvy Blue MOT
		This `curvy_blue_mot` config is for optimizing the mot, via changing the ramp to an arbitrary piecewise linear ramp.
		Here we aim to change only the 
		 * blue mot detuning
		 * blue mot intensity
		 * bias fields
		all synchronously.

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

	# duration = 5;
	timescale = 1;
	# num_parameters = int(duration/timescale)
	num_parameters = 5
	#parameters to optimize
	#come up with names already not in use.
	input_params = {
		"LS_blue_mot_duration":	{"min":0.1,
		                       	"max": 5,
		                       	"start": 5,
		                       	"end": 5,
		                       	"multiple":False,
		                       	"num_parameters":1},

		"x_bias_field_initial":	{"min":-1,
		                       	"max": 6,
		                       	"start": -0.608,
		                       	"end": -0.608,
		                       	"multiple":False,
		                       	"num_parameters":1},
		"y_bias_field_initial":	{"min":1,
		                       	"max":2,
		                       	"start": 1.374,
		                       	"end": 1.374,
		                       	"multiple":False,
		                       	"num_parameters":1},
		"z_bias_field_initial":	{"min":1,
		                       	"max":3,
		                       	"start": 2.2,
		                       	"end": 2.2,
		                       	"multiple":False,
		                       	"num_parameters":1},


		"MLOOP_slow_blue_mot_intensity":  	{"min":0,
		                                  	"max":0.4,
		                                  	"start": 0.38,
		                                  	"end": 0.38,
		                                  	"multiple":True,
		                                  	"num_parameters":num_parameters},
		"MLOOP_slow_blue_mot_x_bias":     	{"min":-1,
		                                  	"max":6,
		                                  	"start":-0.608,
		                                  	"end":-0.608,
		                                  	"multiple":True,
		                                  	"num_parameters":num_parameters},
		"MLOOP_slow_blue_mot_y_bias":     	{"min":1,
		                                  	"max":2,
		                                  	"start":1.374,
		                                  	"end":1.374,
		                                  	"multiple":True,
		                                  	"num_parameters":num_parameters},
		"MLOOP_slow_blue_mot_z_bias":     	{"min":1,
		                                  	"max":3,
		                                  	"start":2.2,
		                                  	"end":2.2,
		                                  	"multiple":True,
		                                  	"num_parameters":num_parameters},
		# "MLOOP_fast_blue_mot_detuning": 	{"min":0.9,
		#                                 	"max":1.1,
		#                                 	"start":,
		#                                 	"end":,
		#                                 	"multiple":True,
		#                                 	"num_parameters":num_parameters},
		# "MLOOP_fast_blue_mot_intensity":	{"min":0.9,
		#                                 	"max":1.1,
		#                                 	"start":,
		#                                 	"end":,
		#                                 	"multiple":True,
		#                                 	"num_parameters":num_parameters},
		# "MLOOP_fast_blue_mot_x_bias":   	{"min":0.9,
		#                                 	"max":1.1,
		#                                 	"start":,
		#                                 	"end":,
		#                                 	"multiple":True,
		#                                 	"num_parameters":num_parameters},
		# "MLOOP_fast_blue_mot_y_bias":   	{"min":0.9,
		#                                 	"max":1.1,
		#                                 	"start":,
		#                                 	"end":,
		#                                 	"multiple":True,
		#                                 	"num_parameters":num_parameters},
		# "MLOOP_fast_blue_mot_z_bias":   	{"min":0.9,
		#                                 	"max":1.1,
		#                                 	"start":,
		#                                 	"end":,
		#                                 	"multiple":True,
		#                                 	"num_parameters":num_parameters},

	}

	#update initial values of parameters with last known working values
	input_params  = update_start_values(initial_globals_file, input_params)

	
	#create the mloop config file
	output = create(input_params)

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
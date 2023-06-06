''' File to Create Configuration for Many Parameters for MLOOP Optimization.

'''
import os
import json
import configparser

MLOOP_archive_folder = r"C:\Users\YbMinutes\labscript-suite\userlib\labscriptlib\ybclock\analysis\analysislib-mloop\M-LOOP_archives"
MLOOP_logs_folder = r"C:\Users\YbMinutes\labscript-suite\userlib\labscriptlib\ybclock\analysis\analysislib-mloop\M-Loop_logs"


def create(input_params, begin_vals=None, load_from_begin_vals=False, config_path=None, rescale=True):
	"""Creates config file from specified file, or
	creates one locally with default values.

	Parameters:
		input_params        	:	is a dictionary of the variables to be scanned over.
		                    	 	Takes keys: "min", "max" -- bounds
		                    	 		"start","end" -- for a ramp
		                    	 		"multiple" -- whether or not to ramp
		                    	 		"num_parameters" -- number of points in the ramp
		num_parameters      	:	if >1, creates a number of variables with the same name 
		                    	 	with a number appended to it i.e., <param_name>XX. If 
		                    	 	num_parameters > 1, I will denote that as a RAMP. This is a key in input_params.
		begin_vals          	:	if you want to redefine the RAMP, you specify begin_vals.
		load_from_begin_vals	:	toggles whether or not to use begin_vals,
		config_path         	:	the path for the resulting .ini file.
		rescale             	:	???
	"""

	# Default to local directory and default name
	if not config_path:
		folder = os.path.dirname(__file__)
		config_path = os.path.join(folder, "mloop_config_GreenMOT.ini")

	# Instantiate RawConfigParser with case sensitive option names
	config = configparser.RawConfigParser()
	config.optionxform = str

	# Check if file exists and initialise with defaults if it does not
	# if os.path.isfile(config_path):
	#     # Retrieve configuration parameters
	#     config.read(config_path)
	# else:
	print("--- Configuration file not found: generating with default values ---")

	# Shot compilation parameters
	config["COMPILATION"] = {}
	config["COMPILATION"]["mock"] = 'false'

	# Analayis parameters
	config["ANALYSIS"]              	= {}
	config["ANALYSIS"]["cost_key"]  	= '["generate_cost", "Cost"]'	# lyse DataFrame key to optimise
	config["ANALYSIS"]["maximize"]  	= 'true'                     	# Maximize cost_key (negate when reporting cost)
	config["ANALYSIS"]["ignore_bad"]	= 'true'                     	# Don't report to M-LOOP if a shot is deemed bad
	# Control log level for logging to console from analysislib-mloop. Not to be
	# confused with MLOOP's console_log_level option for its logger.
	config["ANALYSIS"]["analysislib_console_log_level"] = '"INFO"'
	# Control log level for logging to file from analysislib-mloop. Not to be
	# confused with MLOOP's file_log_level option for its logger.
	config["ANALYSIS"]["analysislib_file_log_level"] = '"DEBUG"'





	# M-LOOP parameters
	config["MLOOP"] = {}

	# Parameters mloop varies during optimisation
	param_string = "{ "
	for key_num, key in enumerate(input_params.keys()):
		param_dict = input_params[key]
		if param_dict["multiple"]:
			num_parameters = param_dict["num_parameters"]
			for i in range(num_parameters):
				min_val = param_dict["min"]
				max_val = param_dict["max"]

				if not load_from_begin_vals:
					begin_val = param_dict['start'] + i * (param_dict['end'] - param_dict['start']) / num_parameters
				if load_from_begin_vals:
					if rescale:
						begin_val = begin_vals[i] * (max_val-min_val) + min_val
					else:
						begin_val = begin_vals[i]
				param_string += '"{}{:02d}": {{"min":{}, "max":{}, "start":{} }}, '.format(key, i, min_val, max_val, begin_val)


		elif not param_dict['multiple']:
			min_val = param_dict["min"]
			max_val = param_dict["max"]
			begin_val = param_dict['start']
			param_string += '"{}": {{"min":{}, "max":{}, "start":{} }}, '.format(key, min_val, max_val, begin_val)
	# get rid of last comma and add end bracket
	param_string = param_string[:-2] + "}"
	# print(param_string)




	config["MLOOP"]["mloop_params"]                      	= param_string
	config["MLOOP"]["num_training_runs"]                 	= '150'  	# Number of training runs
	config["MLOOP"]["max_num_runs_without_better_params"]	= '300'  	# Maximum number of iterations
	config["MLOOP"]["max_num_runs"]                      	= '800'  	# Maximum number of iterations
	config["MLOOP"]["trust_region"]                      	= '0.5'  	# Maximum % move distance from best params
	config["MLOOP"]["cost_has_noise"]                    	= 'true' 	# Maximum number of iterations
	config["MLOOP"]["no_delay"]                          	= 'false'	# Force mloop to return a parameter prediction before it is ready
	config["MLOOP"]["visualisations"]                    	= 'false'	# Display visualisations
	# Type of learner to use in optimisation:
	#   [gaussian_process, random, nelder_mead, neural_net]
	config["MLOOP"]["controller_type"]            	= '"neural_net"'  
	config["MLOOP"]["console_log_level"]          	= '10'	# Mute output from MLOOP optimiser
	config["MLOOP"]['controller_archive_filename']	= os.path.join(MLOOP_archive_folder, 'controller')
	config["MLOOP"]['learner_archive_filename']   	= os.path.join(MLOOP_archive_folder, 'learner')
	config["MLOOP"]['log_filename']               	= os.path.join(MLOOP_logs_folder,'logs')

	# Write to file
	folder = os.path.dirname(__file__)
	with open(os.path.join(folder, "mloop_config.ini"), "w+") as f:
		config.write(f)

	# iterate over configuration object and store pairs in parameter dictionary
	params = {}
	for sect in config.sections():
		for (key, val) in config.items(sect):
			try:
				params[key] = json.loads(val)
			except json.JSONDecodeError:
				params[key] = val

	
	params["cost_key"]  	= tuple(params["cost_key"])  	# Convert cost_key to tuple
	params["num_params"]	= len(params["mloop_params"])	# store number of parameters for passing to controller interface
	# get the names of the parameters, if not explicitly specified by user
	if "param_names" not in params:
		params["param_names"] = list(params["mloop_params"].keys())

	
	params["min_boundary"]	= [param["min"] for param in params["mloop_params"].values()]	# get min boundaries for specified variables
	params["max_boundary"]	= [param["max"] for param in params["mloop_params"].values()]	# get max boundaries for specified variables

	# starting point for search space, default to half point if not defined
	params["first_params"] = [
		param["start"] for param in params["mloop_params"].values()
	]

	return params

globals_file=r"C:\Users\YbMinutes\labscript-suite\userlib\labscriptlib\ybclock\globals.h5"

def create_global(name,value,groupname):
	''' Creates a global in our globals file with name 'name' and value <value>.'''
	try:
		import runmanager as rm 
		rm.new_global(
			filename=globals_file,
			groupname=groupname,
			globalname=name
		)
		rm.set_value(
			filename=globals_file,
			groupname=groupname,
			globalname=name,
			value=value
		)
	except Exception as e:
		print(f"::[{name},{value}]:: {e}")

def create_globals(name_list,values=None):
	''' creates globals in name_list '''
	try:
		import runmanager as rm
		for i in range(len(name_list)):
			name = name_list[i]
			if values is None:
				create_global(name, value=0,groupname='MLOOP')
			else:
				create_global(name, value=values[i],groupname='MLOOP')
	except Exception as e:
		print(e)

def delete_MLOOP_globals(globals_name):
	''' Delete all globals under the group name 'MLOOP' '''
	import runmanager as rm 
	try:
		rm.delete_group(globals_file, globals_name)
	except Exception as e:
		print(e)
	try:
		rm.new_group(globals_file,globals_name)
	except Exception as e:
		print(e)

def repack_globals():
	#variables for repacking the globals file
	userProfile      	= "C:\\Users\\YbMinutes"
	globals_file     	= os.path.join(userProfile,"labscript-suite\\userlib\\labscriptlib\\ybclock\\globals.h5")
	hdf5repack_file  	= os.path.join(userProfile,r"labscript-suite\userlib\labscriptlib\ybclock\feedback\h5repack.exe")
	temp_globals_file	= os.path.join(userProfile,r"labscript-suite\userlib\labscriptlib\ybclock\temp_globals.h5")

	#repack the globals
	print("Repacking Globals...",end="")
	os.rename(globals_file, temp_globals_file)
	os.system(f'{hdf5repack_file} {temp_globals_file} {globals_file}')
	os.remove(temp_globals_file)
	print("Done!")


if __name__ == "__main__":

	input_params = {
		"TRANSFER_x_bias_field":{"min":-1.5, "max": 5.7, "start": 1.3, "end": 5.29, "multiple":True, "num_parameters":6},
		"TRANSFER_y_bias_field":{"min":-.5, "max": 0.8, "start": -0.15, "end": 0.32, "multiple":True, "num_parameters":6},
		"TRANSFER_z_bias_field":{"min":-1, "max": 1, "start": 0, "end": -0.80, "multiple":True, "num_parameters":6},
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
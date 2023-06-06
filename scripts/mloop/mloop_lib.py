'''

	#Info
	File to Create Configuration for Many Parameters for MLOOP Optimization.
	
	This was the first proof of principle script... Use it as a template!!!

	This script was gifted to me by Rydberg Lab. Specifically Matt. Thanks to Zak and Matt...

	I've added improvements. This script initially just created the
	`mloop_config.py` file. My improvements now also automatically modify
	the globals file that runmanager reads. This is accomplished with the functions:

		create_global()
		create_globals()
		delete_MLOOP_globals()
		repack_globals()

	#How this Works

	This program stores the automatically generated variables in a subgroup of
	`optimization.h5` called `'MLOOP'`. This is to prevent cluttering the user
	generated groups.

	So that `mloop_utils.py` in the `subsequences` folder, can automatically
	these variables in, it also stores a variable which holds the name of
	the automatically generated variables. This variable is stored in
	`'MLOOP_VARS'`.

	Upon execution, it deletes these groups if they exist and then repopulates it.
	

'''

import os
import json
import configparser

initial_globals_file=r"C:\Users\YbClockReloaded\labscript-suite\userlib\labscriptlib\ybclock\globals.h5"
cavity_scan_globals_file=r"C:\Users\YbClockReloaded\labscript-suite\userlib\labscriptlib\ybclock\cavity_globals.h5"
globals_file=r"C:\Users\YbClockReloaded\labscript-suite\userlib\labscriptlib\ybclock\optimization.h5"
MLOOP_archive_folder = r"C:\Users\YbClockReloaded\labscript-suite\userlib\labscriptlib\ybclock\analysis\analysislib-mloop\M-LOOP_archives"
MLOOP_logs_folder = r"C:\Users\YbClockReloaded\labscript-suite\userlib\labscriptlib\ybclock\analysis\analysislib-mloop\M-Loop_logs"

try:
	
	pass
except:
	pass
def get_runs_from_time(h=0,m=0):
	print(f"Calculating runs from {h:02}h:{m:02}m duration")
	runs_per_minute = 244/60
	m += 60*h
	return m*runs_per_minute

def create(input_params, learner='neural_net', begin_vals=None, load_from_begin_vals=False, config_path=None, rescale=True, max_num_runs=5, max_num_runs_without_better_params=2):
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
	config["MLOOP"]["num_training_runs"]                 	= '3'                                    	# Number of training runs
	config["MLOOP"]["max_num_runs_without_better_params"]	= str(max_num_runs_without_better_params)	# Maximum number of iterations
	config["MLOOP"]["max_num_runs"]                      	= str(max_num_runs)                      	# Maximum number of iterations
	config["MLOOP"]["trust_region"]                      	= '0.5'                                  	# Maximum % move distance from best params
	config["MLOOP"]["cost_has_noise"]                    	= 'true'                                 	# Maximum number of iterations
	config["MLOOP"]["no_delay"]                          	= 'false'                                	# Force mloop to return a parameter prediction before it is ready
	config["MLOOP"]["visualisations"]                    	= 'false'                                	# Display visualisations
	# Type of learner to use in optimisation:
	#   [gaussian_process, random, nelder_mead, neural_net]
	config["MLOOP"]["controller_type"]            	= f'"{learner}"'
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




def create_global(name,value,groupname):
	''' Creates a global in our globals file with name 'name' and value <value> in the groupname <groupname>.'''
	try:
		import runmanager as rm 
		try:
			rm.new_global(
				filename=globals_file,
				groupname=groupname,
				globalname=name
			)
		except Exception as e:
			print(f"{name} already exists. Updating value.")
		rm.set_value(
			filename=globals_file,
			groupname=groupname,
			globalname=name,
			value=value
		)
	except Exception as e:
		print(f"::[{name},{value}]:: {e}")

def get_existing_globals(globals_file):
	''' A function which returns a list of variables stored in the globals file that is not in MLOOP or MLOOP_VARS '''
	import runmanager as rm
	grouplist = rm.get_grouplist(globals_file)
	try:
		grouplist.remove('MLOOP')
	except:
		pass
	try:
		grouplist.remove('MLOOP_VARS')
	except:
		pass
	groupdict = {}

	for key in grouplist:
		groupdict[key] = globals_file
	_globals = rm.get_globals(groups=groupdict)
	return _globals
	
def create_globals(name_list,groupnames,values=None):
	''' 
		creates globals in name_list which is a list of to algorithmicly
		generated variables. If they exist, just update their value.
	'''
	try:
		import runmanager as rm
		for i in range(len(name_list)):
			name = name_list[i]
			if name in groupnames:
				groupname = groupnames[name]
			else:
				groupname = 'MLOOP'
			# if name not in groupnames:
			if values is None:
				create_global(name, value=0,groupname=groupname)
			else:
				create_global(name, value=values[i],groupname=groupname)
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

def repack_globals(globals_file):
	#variables for repacking the globals file
	userProfile      	= "C:\\Users\\YbClockReloaded"
	# globals_file   	= os.path.join(userProfile,"labscript-suite\\userlib\\labscriptlib\\ybclock\\globals.h5")
	hdf5repack_file  	= os.path.join(userProfile,r"labscript-suite\userlib\labscriptlib\ybclock\feedback\h5repack.exe")
	temp_globals_file	= os.path.join(userProfile,r"labscript-suite\userlib\labscriptlib\ybclock\temp_globals.h5")

	#repack the globals
	print("Repacking Globals...",end="")
	os.rename(globals_file, temp_globals_file)
	os.system(f'{hdf5repack_file} {temp_globals_file} {globals_file}')
	os.remove(temp_globals_file)
	print("Done!")

def find_groupnames(name_list):
	existing_globals_dict = get_existing_globals(initial_globals_file)

	return group_names


def update_start_values(globals_file, input_params):
	''' Replaces the start values with ones from globals file if they already exist '''
	_globals = get_existing_globals(globals_file)
	groupnames_of_input_params = {}
	for GROUP in _globals:
		group_dict = _globals[GROUP]
		for input_param in input_params:
			if input_param in group_dict:
				start_value = eval(group_dict[input_param][0])
				print(f"Found start value for {input_param}: {start_value}")
				input_params[input_param]["start"] = start_value
				groupnames_of_input_params[input_param] = GROUP
	return input_params

def get_groupnames(globals_file, input_params):
	_globals = get_existing_globals(globals_file)
	groupnames_of_input_params = {}
	for GROUP in _globals:
		group_dict = _globals[GROUP]
		for input_param in input_params:
			if input_param in group_dict:
				groupnames_of_input_params[input_param] = GROUP
	return groupnames_of_input_params

def update_globals(input_params, config_dict,group_names=None):
	'''
		Creates MLOOP globals if they don't exist in 'MLOOP'/'MLOOP_VARS'.
		Else, updates the values.

		group_names is a dictionary of the parameters that already exist, with key value parameters.
	'''

	#deletes old variables if generated.
	delete_MLOOP_globals("MLOOP")
	delete_MLOOP_globals("MLOOP_VARS")

	#creates the globals in the MLOOP folder if they dont already exist. and updates if they do.
	create_globals(
		name_list=config_dict['param_names'],
		values=config_dict['first_params'],
		groupnames=get_groupnames(
				globals_file=initial_globals_file,
				input_params=config_dict['param_names']
			)
	)

	#save the mloop_vars_dict for use by the mloop_utils.py ybclock library.
	mloop_vars_dict = {}
	for key in input_params:
		mloop_vars_dict[key] = input_params[key]["num_parameters"]

	create_global('mloop_vars_dict',repr(json.dumps(mloop_vars_dict)),'MLOOP_VARS') #you need the str() so it doesn't store as a list of lists.

def update_drifting_variables():
	''' Update variables that drift '''
	import runmanager
	_vars = {
		'bridging_frequency_759'  	:'Cavity Properties',
		'exp_cavity_set_frequency'	:'Feedback Variables'
	}

	for _variable in _vars:
		_group = _vars[_variable]
		print(f"Updating {_variable} in {_group}")
		x = runmanager.get_value(initial_globals_file, _group, _variable)
		runmanager.set_value(globals_file, _group, _variable, x)

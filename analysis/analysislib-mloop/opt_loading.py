
def opt_loading_config():
	#settings are stored in s.
	s = {}

	#COMPILATION
	s['mock']	= False

	#ANALYSIS
	s['cost_key']	= ['generate_cost', 'Neta']
	s['maximize']	= True
	s['ignore_bad'] = True

	#MLOOP
	s['mloop_params']	=  {
	                 	'blue_mot_duration': {'min': 0.1, 'max': 3.0, 'start': 0.2},
	}

	s['num_training_runs']	= 50
	s['trust_region']     	= 0.5
	s['cost_has_noise']   	= True
	s['controller_type']  	= 'gaussian_process'
	s['visualisations']   	= True

	return s



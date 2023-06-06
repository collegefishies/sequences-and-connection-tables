from labscriptlib.ybclock.analysis.functions import multiprocess_fit_functions as fit_functions
from labscriptlib.ybclock.analysis.functions.metadata import extract_sequence_repetition_numbers, extract_date,extract_sequence_name

import numpy as np
import pickle

import matplotlib.pyplot as plt

def parse_scan_parameters(scan_params_dict):
	# scan_params_dict is a dictionary whose properties are defined in exp_cavity.py
	start_time	= scan_params_dict['t']
	end_time  	= start_time + scan_params_dict['duration']
	final_f   	= scan_params_dict['final_f']
	initial_f 	= scan_params_dict['initial_f']

	return start_time, end_time, final_f, initial_f

def select_photons_in_scan(photon_arrival_times, start_time, end_time):
	''' selects photons within a certain interval. everything is in arrival times.'''
	
	scan_photons = photon_arrival_times[
		(photon_arrival_times > start_time) & (photon_arrival_times < end_time)
	]
	total_photons = len(scan_photons)

	return scan_photons, total_photons

def convert_arrival_time_to_frequency(photon_arrival_times, initial_f, final_f, start_time, end_time):
	#Extract photon's frequency based on arrival time
	#since we have calibrated frequency vs voltage, and performed the scan across frequency
	#there is a true linear relationship between arrival time and frequency :)
	photon_arrivals_in_frequency_MHz = (photon_arrival_times - start_time)*(final_f-initial_f)/(end_time-start_time)+initial_f
	return photon_arrivals_in_frequency_MHz



def plot_photons_as_histogram(photon_frequencies, bin_width,plt,data_globals):
	bin_boundaries = np.arange(
				data_globals["empty_cavity_frequency_sweep_initial"],
				data_globals["empty_cavity_frequency_sweep_range"], 
				bin_width
			)

	plt.hist(
		photon_frequencies,
		bins=bin_boundaries,
		align='mid'
	)

	plt.set_ylabel('Photon Counts')
	plt.set_xlabel('Frequency (MHz)')

def plot_photon_rabi_splitting_as_histogram(photon_frequencies,data_globals,bin_width, time, Neta, plt):
	#plot histogram	
	#plot data
	bin_boundaries = np.arange(
				data_globals["empty_cavity_frequency_sweep_initial"],
				data_globals["empty_cavity_frequency_sweep_range"], 
				bin_width
			)
	plt.hist(
		photon_frequencies,
		bins=bin_boundaries,
		align='mid',
		label=f"Time: {time:.3f}, Neta: {Neta:.0f}"
	 )

	plt.legend()

def plot_photon_rabi_splitting_as_histogram_DEBUG(photon_frequencies,data_globals,bin_width, Neta, fcav, fatom, plt):
	#plot histogram	
	#plot data
	# write Neta, fcavity and fatoms from the fits
	bin_boundaries = np.arange(
				data_globals["empty_cavity_frequency_sweep_initial"],
				data_globals["empty_cavity_frequency_sweep_range"], 
				bin_width
			)
	plt.hist(
		photon_frequencies,
		bins=bin_boundaries,
		align='mid',
		label=f"f_cavity: {fcav:.3f}, f_atoms: {fatom:.3f}, Neta: {Neta:.0f}"
	 )

	plt.legend()

def check_photon_number(**kwargs):
	'''
		Takes in the `total_number_of_photons` and the `minimum_number_of_photons` to check validity.
	'''

	if kwargs['total_number_of_photons'] > kwargs['minimum_number_of_photons']:
		return True
	else:
		return False

def is_valid_scan(**kwargs):
	is_valid = True
	is_valid = is_valid and check_photon_number(**kwargs)

	return is_valid	

def decide_to_use_MAXIMUM_LIKELIHOOD_ESTIMATOR(total_photon_number, photon_threshold):
	return total_photon_number < photon_threshold

def fit_using_least_squares(photon_frequencies, bin_width, DEBUG=False):
	'''
		Returns the fitted parameters of the least square fit of the Lorentzian to the data. 
	'''

	try:
		fitted_parameters = fit_functions.fit_single_cavity_peak(
						data        	=photon_frequencies,
						start       	=np.min(photon_frequencies),
						end         	=np.max(photon_frequencies), 
						bin_interval	=bin_width,
					)
		if DEBUG:
			print("Empty Cavity Fit Params:")
			for key, value in fitted_parameters.items():
				if key not in "covariance matrix":
					print(f"{key}: {value}")
		
		return fitted_parameters
	except Exception as e:
		import traceback
		import sys
		print("Least_square Photon Arrival Time Fit Failed.Error : ")
		traceback.print_exception(*sys.exc_info())
		return None


def fit_using_maximum_likelihood_estimator(photon_frequencies, bin_width, data_globals, DEBUG=False):
	#Fit the Data using the MLE method.
	try:
		fitted_parameters = fit_functions.fit_single_cavity_peak_MLE(
			data=photon_frequencies,
			#Each lower bound must be strictly less than each upper bound. Use fatom_range == fcavity_range to avoid any possible error.
			data_globals=data_globals,
			bin_interval=bin_width,
		)
		if DEBUG:
			print("Empty Cavity Fit Params:")
			for key, value in fitted_parameters.items():
				if key not in 'covariance':
					print(f"{key}: {value}")

		return fitted_parameters
	except Exception as e:
		import traceback
		import sys
		print("MLE Photon Arrival Time Fit Failed! Error : ",e)
		# print("Least_square Photon Arrival Time Fit Failed.Error : ")
		traceback.print_exception(*sys.exc_info())
		return None

def fit_splitting_using_least_squares(photon_frequencies, cavity_range, bin_width,data_globals, DEBUG=False):
	'''
		Returns the fitted parameters of the least square fit of the splitting to the data. 
	'''

	#Fit the Data using the least_square method. We should find out after which photon_number the least_suare approach is significantly faster than MLE (for n~400 MLE is extra-ordinarely faster)
	# Remember to add fatom_guess in globals!
	try:
		best_param = fit_functions.fit_rabi_splitting_transmission(
			data = photon_frequencies,
			bnds={"fatom_range":(0,50), "fcavity_range":cavity_range, "Neta_range":(0,10000)},
			bin_interval=bin_width,
			data_globals=data_globals,
			)
		if DEBUG:
			print("Rabi Splitting Fit Params:")
			for key, value in best_param.items():
				if key not in "jacobian":
					print(f"{key}: {value}")
		return best_param
	except Exception as e:
		import traceback
		import sys
		traceback.print_exception(*sys.exc_info())

def fit_splitting_using_maximum_likelihood_estimator(photon_frequencies, bin_width,cavity_range, data_globals, DEBUG=False):
	try:
		best_param = fit_functions.fit_rabi_splitting_transmission_MLE(
			data=photon_frequencies, 
			bnds={"fatom_range":(0,50), "fcavity_range":cavity_range, "Neta_range":(0,20000)},
			bin_interval=bin_width,
			param_error = 'off',
			data_globals=data_globals,
		)
		if DEBUG:
			print("Rabi Splitting Fit Params:")
			for key, value in best_param.items():
				if key not in 'covariance':
					print(f"{key}: {value}")
		return best_param
	except Exception as e:
		import traceback
		import sys
		traceback.print_exception(*sys.exc_info())

def fit_using_gaussian_mixture_model(photon_frequencies, bin_width = None,cavity_range = None, data_globals=None, DEBUG=False,plt=None):
	from sklearn.mixture import GaussianMixture, BayesianGaussianMixture

	# def bin_photon_data(photon_frequencies,bin_width, cavity_range):
	#	#no need to bin the data! gaussian mixture takes in many samples
	#	bins = (cavity_range[1] - cavity_range[0])/bin_width
	#	X,bin_edges = np.histogram(photon_frequencies, bins=bins, range=cavity_range)
	#	return X 
	weights = None
	def weight_by_distance(photon_frequencies):
		'''
			Calculates the sum of all distances from all other photons, and
			weights by 1 over that distance. This penalizes lonely photons.
			Doesn't work, Gaussian mixture just wants the weights of the gaussians.
		'''
		weights = []
		for i in range(len(photon_frequencies)):
			photon_f = photon_frequencies[i]
			distance = np.linalg.norm(np.array(photon_frequencies) - photon_f)
			weights.append(distance)
		return weights

	weights = weight_by_distance(photon_frequencies)
	# X = bin_photon_data(photon_frequencies, bin_width, cavity_range)
	X = np.array(photon_frequencies).reshape(-1,1)
	X = np.transpose(np.vstack((photon_frequencies, weights)))

	gm = GaussianMixture(
		n_components=3,	#number of gaussians to try to fit
		random_state=0,	#random seed for the fitter
		# covariance_type='tied',
		max_iter=100,
	).fit(X)

	if plt:
		X = np.transpose(X)
		x = X[0]
		y = X[1]
		print(len(x))
		plt.scatter(x,y,s =1)
		plt.xlabel('Frequency (MHz)')
		plt.ylabel('Distance')
		# plt.clear()
		pass


	# print("MEANS:")
	# print(gm.means_)
	# print("covariances_")
	# print(gm.covariances_)
	# print(f"Converged? : {gm.converged_}")
	return gm.means_, gm.covariances_

def plot_gaussian_mixture_model_fit(means, covariances, amplitude, plt, data_globals,bin_width):
	x = np.arange(
			data_globals["empty_cavity_frequency_sweep_initial"],
			data_globals["empty_cavity_frequency_sweep_range"], 
			bin_width
	)

	freq_means = []
	freq_errs = []
	for component in range(len(means)):
		#loops through each gaussian
		gaussian_means = means[component]
		gaussian_covariances = covariances[component]

		freq_mean = gaussian_means[0]
		freq_err  = np.sqrt(np.diag(gaussian_covariances)[0])

		freq_means.append(freq_mean)
		freq_errs.append(freq_err)

	means = freq_means
	variances = np.square(freq_errs)
	def g(x, mean, variance):
		e = np.exp(1)
		return 1/np.sqrt(6.28*variance)*(np.sqrt(e))**(-(x-mean)**2/variance) #moments form of a gaussian
	g_func = 0
	for i in range(len(means)):
		g_func += g(x, means[i], variances[i])
	model = amplitude*g_func
	plt.plot(x,model,label='GMM Fit')
	pass
def label_plots(bin_width, hdf_path):
	#extract metadata
	(sequence_number, repetition_number)	= extract_sequence_repetition_numbers(hdf_path)
	date                                	= extract_date(hdf_path)
	sequence_name                       	= extract_sequence_name(hdf_path)
	                                    		

	# print(len(photon_arrivals_in_frequency_MHz))
	
	#decorate plot
	plt.suptitle(f"({date}) #{sequence_number}_r{repetition_number}\n{sequence_name}")
	plt.ylabel(f"Photon Counts, ({bin_width*1000:.3g} kHz Bin)")
	plt.xlabel("Frequency (MHz)")

def fit_using_Clustering(photon_frequencies, bin_width = None,cavity_range = None,  data_globals=None, DEBUG=False,plt=None):
	# from sklearn.mixture import GaussianMixture, BayesianGaussianMixture
	kappa_loc = 0.530
	gamma_loc = 0.184

	eps = (kappa_loc*gamma_loc)**(0.5)/2

	data, dist_peaks = fit_functions.find_peaks(photon_frequencies=photon_frequencies, eps=eps)
	
	distribution, frequency_axis = fit_functions.calculate_histogram(
		photon_frequencies=data,
		frequency_range=(data[0], data[-1]),
		bin_width=0.2
		)

	Neta_guess = dist_peaks**2/(kappa_loc*gamma_loc)

	POWER = 2
	distribution = fit_functions.square_distribution(distribution,frequency_axis[:-1],POWER)
	skew, var, mean = fit_functions.return_moments(distribution,frequency_axis[:-1])

	diff_cavity_atoms = -(skew/var)/2.5;
	fcavity_guess = mean
	fatoms_guess = fcavity_guess-diff_cavity_atoms
	if plt:
		bin_boundaries = np.arange(
				-10,
				40, 
				0.45
			)
		plt.hist(
			data,
			bins=bin_boundaries,
			align='mid',
			label=f"f_cavity: {fcavity_guess:.3f}, Neta: {Neta_guess:.0f}"
			 )
		pass
	return Neta_guess, fcavity_guess, fatoms_guess

def plot_fitted_curves(photon_frequencies, fitted_parameters,bin_width,plt,data_globals):
	try:
		bin_boundaries = np.arange(
			data_globals["empty_cavity_frequency_sweep_initial"],
			data_globals["empty_cavity_frequency_sweep_range"], 
			bin_width
		)

		y = fit_functions.lorentzian(
				x = bin_boundaries,
				x0 = fitted_parameters["fcavity"],
				gamma = fitted_parameters["kappa"],
				a = fitted_parameters["amplitude"],
				offset = fitted_parameters["dark_counts"],
			)
		plt.plot(bin_boundaries,y)
	except Exception as e:
		import traceback
		import sys
		traceback.print_exception(*sys.exc_info())


def plot_rabi_splitting_fitted_curves(photon_frequencies, fitted_parameters, bin_width, plt, data_globals):
	#plot fit
		try:
			bin_boundaries = np.arange(
				data_globals["empty_cavity_frequency_sweep_initial"],
				data_globals["empty_cavity_frequency_sweep_range"], 
				bin_width
			)
		
			y = fit_functions.rabi_splitting_transmission(
					f = bin_boundaries,
					fatom = fitted_parameters["fatom"],
					fcavity = fitted_parameters["fcavity"],
					Neta = fitted_parameters["Neta"],
					gamma = fitted_parameters["gamma"],
					kappa = fitted_parameters["kappa"]
				)
			try:
				plt.plot(bin_boundaries,fitted_parameters["amplitude"]*y)
			except Exception as e:
				plt.plot(bin_boundaries,1/0.6*sum(n[0])*bin_width*y)
				print("amplitude fit parameter not found:", e)
		except Exception as e:
			import traceback
			import sys
			traceback.print_exception(*sys.exc_info())

		try:
			#store all the results in a dictionary
			parameters = best_param
			#add all the scan_parameters to the dictionary
			parameters.update(a_scan)
			results_to_save.append(parameters)
		except:
			pass

def combine_fitted_parameters_and_scan_parameters(fitted_parameters,scan_parameters):
	parameters = fitted_parameters
	parameters.update(scan_parameters)

	return parameters

def save_parameters_and_documentation(results_to_save,run, DEBUG=False):
	#save some documentation with the parameters
	docstring = '''

	Fit results are saved to a list. Each element represents an
	empty_cavity_scan. Each element is a dictionary that holds all the
	parameters describing the fit results. Pull the keys to see the fit values.

	To extract the data use python3.8, pickle and numpy, and lyse.

	void_pickled_dict_list = run.get_result_array(group='_scan_analysis_name_.py',
	name='')
	pickled_dict_list = void_pickled_dict.tobytes()
	fit_parameter_list = pickle.loads(pickled_dict_list)

	'''

	#save all parameters
	pickled_dict_list = pickle.dumps(results_to_save)
	run.save_result_array(
		name='fitted_exp_cavity_frequency_parameters',
		data=np.void(pickled_dict_list),
		# group=script_name + ''
	)
	
	#save some documentation
	run.save_result(
		name='documentation_fitted_exp_cavity_frequency_parameters',
		value=docstring,
		# group=script_name + '/fitted_exp_cavity_frequency_parameters'
	)

	#save averaged sample of the cavity frequency.
	try:
		average_frequency = 0
		number_of_scans = 0
		for each_scan in results_to_save:
			average_frequency += each_scan['fcavity']
			number_of_scans += 1

		average_frequency = average_frequency / number_of_scans
		run.save_result(
			name='exp_cavity_frequency',
			value=average_frequency,
			# group=script_name + ''
		)
	except:
		pass

	# save all fit results
	try:
		# create a single dictionary containing all the fitted data from all scans.
		results_to_save_dic = {}
		for scan_number in range(len(results_to_save)):
			for name, value in results_to_save[scan_number].items():
				newname = name+"_"+str(scan_number+1)
				results_to_save_dic[newname]=value
		# save data from the complete dictionary.
		if DEBUG: print(results_to_save_dic)
		run.save_results_dict(
			results_dict=results_to_save_dic,
			# group=script_name + ''
			)
	except Exception as e:
		import traceback
		import sys
		# print("Least_square Photon Arrival Time Fit Failed.Error : ")
		print("Failed Saving Fit Results in Lyse. Error:", e)
		traceback.print_exception(*sys.exc_info())
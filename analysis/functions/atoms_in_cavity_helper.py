from labscriptlib.ybclock.analysis.functions import fit_functions
import numpy as np
import matplotlib.pyplot as plt
from labscriptlib.ybclock.analysis.functions.metadata import extract_sequence_repetition_numbers, extract_date,extract_sequence_name
from lyse import Run
import pickle
from labscriptlib.ybclock.analysis.functions.cavity_analysis_lib import *

DEBUG = False
DEBUG_Fit = False
minimum_photons = 10
clustering_only = False

def atom_cavity_analysis(data, scan_parameters,path,axs):
	'''

	This script calculates and saves "vacuum" rabi splitting parameters, as well
	as some vestigial parameters that come from the free parameters in the
	fitting function.

	Here we take the photons arrival time (`data`), check which one has arrived within an
	empty cavity scan, and, for each scan, we convert the arrival time into
	photon's frequency. We finally fit each scan.

	We do not perform MLE analysis if we detect enough photons in the scan. "Enough photons" means that MLE and least_square provide the same uncertainty on the atom number estimation, see [MLE_vs_leastSquare](https://paper.dropbox.com/doc/Fit-and-measurement-quality--BJneIwnJqNOnEEYUYTkog5qxAg-szpYsBrXGK81Qq4BF6jEF) for details.


	The save parameters are stored in "results/empty_cavity_helper/fitted_exp_cavity_frequency_parameters"

	## To Dos

	[] find out for which combination of histogram_resolution and photon number the least_square method becomes significantly faster than MLE without losses in parameter estimations.

	'''

	if DEBUG: print("\n\n\nIn atom_cavity_analysis::");
	results_to_save = []
	#get empty cavity scan parameters from hdf file.
	run = Run(path)
	run.set_group('atoms_in_cavity_helper')
	plot_counter = -1

	#Fit the Data using both least_square method or MLE method.
	try:
		# Check if there is an empty cavity fit and extract empty cavity frequency
		empty_cavity_frequency_from_fit = run.get_result("empty_cavity_helper", "exp_cavity_frequency")
		# When we have atoms in the spin down state, the effective empty cavity
		# frequency is "pushed" up by ~400kHz per 1000 N_downeta, hence the
		# asymmetric bounds 
		cavity_range = (empty_cavity_frequency_from_fit - 0.5, empty_cavity_frequency_from_fit + 1.5);
	except Exception as e:
		cavity_range = (0,50);
		print(f"No empty cavity scan result found. {e}")

	labels = []
	for a_scan in scan_parameters:
		plot_counter += 1
		start_time, end_time, final_f, initial_f	= parse_scan_parameters(
		                                        		scan_params_dict=a_scan
		                                        	)
		scan_photons, total_photons             	= select_photons_in_scan(
		                                        		photon_arrival_times=data,
		                                        		start_time=start_time,
		                                        		end_time=end_time
		                                        	)
		photon_frequencies                      	= convert_arrival_time_to_frequency(
		                                        		photon_arrival_times=scan_photons,
		                                        		initial_f=initial_f,
		                                        		final_f=final_f,
		                                        		start_time=start_time,
		                                        		end_time=end_time
		                                        	)               
		histogram_resolution = .2;
		
		if clustering_only :
			best_param = fit_splitting_using_clustering(
				photon_frequencies, 
				cavity_range=cavity_range, 
				bin_width=histogram_resolution, 
				hdf_path=path, 
				DEBUG=False
			)

		elif not decide_to_use_MAXIMUM_LIKELIHOOD_ESTIMATOR(total_photons,photon_threshold=4000):
			best_param = fit_splitting_using_least_squares(
				photon_frequencies, 
				cavity_range, 
				bin_width=histogram_resolution,
				hdf_path=path,
				DEBUG=False
			)
		else:
			best_param = fit_splitting_using_maximum_likelihood_estimator(
				photon_frequencies, 
				cavity_range=cavity_range, 
				bin_width=histogram_resolution, 
				hdf_path=path, 
				DEBUG=False
			)

		#try the gaussian mixture model
		if DEBUG: 
			print("Trying Gaussian Mixture Model")
			try:
				gm_mean, gm_cov = fit_using_gaussian_mixture_model(
					photon_frequencies,
					# plt=axs[plot_counter]
				)
			except:
				import traceback
				import sys
				traceback.print_exception(*sys.exc_info())
		#try the Clustering model
		if DEBUG_Fit: 
			print("Trying Clustering Model")
			try:
				photon_frequencies.sort()
				fit_using_Clustering(
					photon_frequencies,
					plt=axs[plot_counter]
				)
			except:
				import traceback
				import sys
				traceback.print_exception(*sys.exc_info())

		label_plots(bin_width=histogram_resolution, hdf_path=path)

		if DEBUG: print(f"\t Plotting Photons and Fits... #{plot_counter}")
		PLOT=True
			
		if PLOT:
			try:
				if DEBUG_Fit:
				     plot_photon_rabi_splitting_as_histogram_DEBUG(
				     		photon_frequencies,
				     		bin_width=histogram_resolution,
				     		data_globals=run.get_globals(),
				     		Neta=best_param['Neta'],
				     		fcav=best_param['fcavity'],
				     		fatom=best_param['fatom'],						
				     		plt=axs[plot_counter]
				     	)
				else:				
				     	plot_photon_rabi_splitting_as_histogram(
				     		photon_frequencies,
				     		bin_width=histogram_resolution,
				     		data_globals=run.get_globals(),
				     		time=a_scan['t'],
				     		Neta=best_param['Neta'],
				     		plt=axs[plot_counter]
				     	)

				plot_rabi_splitting_fitted_curves(
					photon_frequencies,
					fitted_parameters=best_param,
					bin_width=histogram_resolution,
					plt=axs[plot_counter],
					data_globals=run.get_globals()
					)

				try:
					# plot_gaussian_mixture_model_fit(
					#	means=gm_mean,
					#	covariances=gm_cov,
					#	amplitude=50,
					#	plt=axs[plot_counter],
					#	data_globals=run.get_globals(),
					#	bin_width=histogram_resolution
					# )
					pass
				except:
				                           	import traceback
				                           	import sys
				                           	traceback.print_exception(*sys.exc_info())
				if DEBUG: print("\t Done.")	
			except:
				import traceback
				import sys
				traceback.print_exception(*sys.exc_info())
		try:
			if DEBUG: print(f"\tSaving results as a dictionary. #{plot_counter}")
			#store all the results in a dictionary
			parameters = best_param
			#add all the scan_parameters to the dictionary
			parameters.update(a_scan)
			results_to_save.append(parameters)
			if DEBUG: print(best_param)
			if DEBUG: print("\tResults cataloged.")
		except:
			import traceback
			import sys
			traceback.print_exception(*sys.exc_info())



	#save fit parameters into hdf file.
	run = Run(path)

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

	pickled_dict_list = pickle.dumps(results_to_save)
	run.save_result_array(
		name='fitted_exp_cavity_frequency_parameters',
		data=np.void(pickled_dict_list)
	)
	run.save_result(
		name='documentation_fitted_exp_cavity_frequency_parameters',
		value=docstring,
		group='empty_cavity_helper/fitted_exp_cavity_frequency_parameters'
	)

	# save all fit results
	try:
		if DEBUG: print(f"\tTrying to save all fitted data... #{plot_counter}")
		# create a single dictionary containing all the fitted data from all scans.
		results_to_save_dic = {}
		for scan_number in range(len(results_to_save)):
			for name, value in results_to_save[scan_number].items():
				newname = name+"_"+str(scan_number+1)
				results_to_save_dic[newname]=value
		# save data from the complete dictionary.
		# if DEBUG: print(results_to_save_dic)
		run.save_results_dict(results_to_save_dic)
		if DEBUG: print("\tDone.")
	except Exception as e:
		print("Failed Saving Fit Results in Lyse. Error:", e)
		import traceback
		import sys
		traceback.print_exception(*sys.exc_info())
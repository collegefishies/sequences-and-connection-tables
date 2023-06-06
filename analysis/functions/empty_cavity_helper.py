import numpy as np
import matplotlib.pyplot as plt
from labscriptlib.ybclock.analysis.functions.cavity_analysis_lib import *
from lyse import Run
from contextlib import suppress

DEBUG = False
minimum_photons = 40
freq_bin_width_MHz = 0.2


def empty_cavity_analysis(data, scan_parameters,path,axs):
	'''

	Here we take the photons arrival time (`data`), check which one has arrived within an
	empty cavity scan, and, for each scan, we convert the arrival time into
	photon's frequency. We finally fit each scan.

	This script saves cavity frequency parameters, as well as some vestigial parameters that
	come from the free parameters in the fitting function.

	The save parameters are stored in "results/empty_cavity_helper/fitted_exp_cavity_frequency_parameters"

	We do not perform MLE analysis if we detect enough photons in the scan. "Enough photons" means that MLE and least_square provide the same uncertainty on the atom number estimation, see [MLE_vs_leastSquare](https://paper.dropbox.com/doc/Fit-and-measurement-quality--BJneIwnJqNOnEEYUYTkog5qxAg-szpYsBrXGK81Qq4BF6jEF) for details.

	# To Dos
	[x] Update Lorentzian fit and Empty cavity fit function
	[x] Use Lorentzian fit in this function. It will save a lot of time
	[x] Implement MLE method with for "simple" Lorentzian fit
	[] Plot if MLE method is used
	[x] Check and implement link to values defined in Globals if necessary

	'''

	results_to_save = []
	#save fit parameters into hdf file.
	run = Run(path)
	run.set_group('empty_cavity_helper')
	plot_counter = -1

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

		#in case the analysis will fail while locking the cavity.
		plot_photons_as_histogram(
			photon_frequencies=photon_frequencies,
			bin_width=freq_bin_width_MHz,
			plt=axs[plot_counter],
			data_globals=run.get_globals()
		)

		if not is_valid_scan(
				total_number_of_photons=total_photons,
				minimum_number_of_photons=minimum_photons,
			):
			#save nan result if not valid.
			run.save_result(
				name='exp_cavity_frequency',
				value=np.nan,
				# group='empty_cavity_helper'		
			)
			continue
			
		if not decide_to_use_MAXIMUM_LIKELIHOOD_ESTIMATOR(total_photons, photon_threshold=4000):
			fitted_parameters = fit_using_least_squares(
					photon_frequencies	= photon_frequencies,
					bin_width         	= freq_bin_width_MHz,
				)
		else:
			fitted_parameters = fit_using_maximum_likelihood_estimator(
					photon_frequencies=photon_frequencies,
					bin_width=freq_bin_width_MHz,
					hdf_path=path
				)

		label_plots(bin_width=freq_bin_width_MHz, hdf_path=path)
		
		plot_fitted_curves(
			photon_frequencies=photon_frequencies,
			fitted_parameters=fitted_parameters,
			bin_width=freq_bin_width_MHz,
			plt=axs[plot_counter],
			data_globals=run.get_globals()
		)


		

		try:
			results_to_save.append(
					combine_fitted_parameters_and_scan_parameters(
						fitted_parameters=fitted_parameters,
						scan_parameters=a_scan
						)
				)
		except:
			pass


		save_parameters_and_documentation(
			results_to_save=results_to_save, 
			run=run
		)



'''

	Loops through the parameters saved by ExperimentalCavity() class and
	performs analysis by passing the 3 parameters needed to an analysis function.

'''
from lyse import path, Run
from pylab import *

#Add in libraries for working with HDF files
import labscript_utils.h5_lock
import h5py

#Add class
from labscriptlib.ybclock.classes import ExperimentalCavity

#analysis libs
import numpy as np
import matplotlib.pyplot as plt
import labscriptlib.ybclock.analysis.functions.fit_functions as fit_functions
from labscriptlib.ybclock.analysis.functions.empty_cavity_helper import empty_cavity_analysis
from labscriptlib.ybclock.analysis.functions.atoms_in_cavity_helper import atom_cavity_analysis
# from labscriptlib.ybclock.analysis.functions.neta_variance_estimator import estimate_neta
from labscriptlib.ybclock.analysis.functions.cavity_analysis_lib import *

import pickle
import time

PLOT = False
DEBUG = False
POWER = 2

def calculate_histogram(photon_frequencies, frequency_range, bin_width):
	f = frequency_range
	bins = int((f[1] - f[0])/bin_width)

	return np.histogram(
			photon_frequencies,
			bins=bins,
			range=frequency_range,
			density=True
		)
def square_distribution(distribution, x_axis,power=2):
	'''
		Squares the probability distribution and then normalizes it.
	'''

	distribution = np.power(distribution,power)
	#integrate
	norm = np.trapz(distribution,x_axis)
	return distribution/norm

def return_std_deviation(distribution,x_axis):
	integrand = np.multiply(distribution,x_axis)
	mean = np.trapz(integrand, x_axis)

	integrand = np.multiply(distribution,np.square(x_axis - mean))
	std_dev = np.trapz(integrand, x_axis)
	return std_dev, mean

def estimate_neta(data, scan_parameters, path, axs):
	''' Calculates neta by using the std. deviation of the square lorentzian distribution. This is Neta + cavity linewidth.	'''
	results_to_save = []
	run = Run(path)
	run.set_group('neta_variance_estimator')
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


		bin_width = .2;	#MHz

		distribution, frequency_axis = calculate_histogram(
			photon_frequencies=photon_frequencies,
			frequency_range=(a_scan['initial_f'], a_scan['final_f']),
			bin_width=bin_width
		)

		distribution = square_distribution(distribution,frequency_axis[:-1],POWER)
		std_dev , mean = return_std_deviation(distribution,frequency_axis[:-1])
		print(std_dev)
		run.save_result(f'std_dev_{plot_counter+1}', std_dev)
		run.save_result(f'start_time_{plot_counter+1}', start_time)
		axs[plot_counter].plot(frequency_axis[:-1], distribution)
		label_plots(bin_width=bin_width, hdf_path=path)
	pass

def main():
	#get data
	run = Run(path)


	#extract cavity_scan_parameters metadata
	try:
		exp_cavity = ExperimentalCavity()
		cavity_scan_parameters = exp_cavity.get_parameters(path)
		if DEBUG:
			print(f'Discovered {len(cavity_scan_parameters)} types of scans: {cavity_scan_parameters.keys()}')
	except:
		print("Error: Could not extract cavity_scan_parameters.")


	#extract photon data
	try:
		photon_arrival_times = run.get_result_array(group='extract_photon_arrival_times',name='processed_arrivals_ch_1')
	except:
		print("Error: Could not extract photon_arrival_times.")


	#check to see if we need to run any sort of cavity analysis
	try:
		#calculate total number of scans
		scan_set = []
		try:
			scan_set = scan_set + cavity_scan_parameters['empty_cavity']
		except:
			pass
		try:
			scan_set = scan_set + cavity_scan_parameters['atoms_in_cavity']
		except:
			pass
		number_of_scans = len(scan_set)
		if PLOT:
			fig, axs = plt.subplots(number_of_scans)
		else:
			fig = None,
			axs = None
		# fig.tight_layout()
		# plt.suptitle()
		empty_cavity_plts = axs[0:len(cavity_scan_parameters['empty_cavity'])]
		start_index = len(cavity_scan_parameters['empty_cavity'])
		atoms_in_cavity_plts = axs[start_index : start_index + len(cavity_scan_parameters['atoms_in_cavity'])]

		for each_key in cavity_scan_parameters.keys():
			if each_key == 'empty_cavity':
				pass

		for each_key in cavity_scan_parameters.keys():
			#we analyse all other cavity scan not empty
			if each_key == 'atoms_in_cavity':
				#monitor the process time
				t0 = time.time()
				try:
					#spot for Neta Variance Estimator
					estimate_neta(
							data=photon_arrival_times, 
							scan_parameters=cavity_scan_parameters[each_key],
							path=path,
							axs=atoms_in_cavity_plts
						)
					pass
				except Exception as e:
					import traceback
					import sys
					print(f"Cavity Scan Type {each_key} Error: {e}")
					traceback.print_exception(*sys.exc_info())
				t = time.time()-t0
				print(f"Time used for atom_cavity_analysis: {t:0.3} sec")
	except Exception as e:
		print(f"Error: {e}")

if __name__ == '__main__':
	main()
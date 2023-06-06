'''

	Loops through the parameters saved by ExperimentalCavity() class and
	performs analysis by passing the 3 parameters needed to an analysis function.

'''
from lyse import *
from pylab import *

#Add in libraries for working with HDF files
import labscript_utils.h5_lock
import h5py

#Add class
from labscriptlib.ybclock.classes import ExperimentalCavity

#analysis libs
import numpy as np
import matplotlib.pyplot as plt
import labscriptlib.ybclock.analysis.functions.multiprocess_fit_functions as fit_functions
from labscriptlib.ybclock.analysis.functions.empty_cavity_helper import empty_cavity_analysis
from labscriptlib.ybclock.analysis.functions.multiprocess_atoms_in_cavity_helper import atom_cavity_analysis
# from labscriptlib.ybclock.analysis.functions.neta_variance_estimator import estimate_neta
import pickle
import time

DEBUG = False

if __name__ == '__main__':
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
		fig, axs = plt.subplots(number_of_scans)
		# fig.tight_layout()
		# plt.suptitle()
		empty_cavity_plts = axs[0:len(cavity_scan_parameters['empty_cavity'])]
		start_index = len(cavity_scan_parameters['empty_cavity'])
		atoms_in_cavity_plts = axs[start_index : start_index + len(cavity_scan_parameters['atoms_in_cavity'])]

		for each_key in cavity_scan_parameters.keys():
			if each_key == 'empty_cavity':
			#we prioritize empty cavity scans
				try:
					empty_cavity_analysis(
						data=photon_arrival_times,
						scan_parameters=cavity_scan_parameters[each_key],
						path=path,
						axs=empty_cavity_plts
					)
				except Exception as e:
					import traceback
					import sys
					print(f"Cavity Scan Type {each_key} Error: {e}")
					traceback.print_exception(*sys.exc_info())

		for each_key in cavity_scan_parameters.keys():
			#we analyse all other cavity scan not empty
			if each_key == 'atoms_in_cavity':
				#monitor the process time
				t0 = time.time()
				try:
					atom_cavity_analysis(
						data=photon_arrival_times,
						scan_parameters=cavity_scan_parameters[each_key],
						path=path,
						axs=atoms_in_cavity_plts
					)
				except Exception as e:
					import traceback
					import sys
					print(f"Cavity Scan Type {each_key} Error: {e}")
					traceback.print_exception(*sys.exc_info())
				try:
					#spot for Neta Variance Estimator
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

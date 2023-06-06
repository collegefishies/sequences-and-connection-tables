####################################################
####################################################
#
#
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
import labscriptlib.ybclock.analysis.functions.fit_functions as fit_functions
from labscriptlib.ybclock.analysis.functions.empty_cavity_helper import empty_cavity_analysis
import pickle

'''
This is a test code where we analyse empty cavities scan in our sequences.

'''
if __name__ == '__main__':
	run = Run(path)

	try:
		#extract cavity_scan_parameters metadata
		exp_cavity = ExperimentalCavity()
		cavity_scan_parameters = exp_cavity.get_parameters(path)

		# print(f"Cavity Scan Parameters:\n\n\n{cavity_scan_parameters}\n\n\n\n")

		#extract globals
		# data_globals = run.get_globals()

		#extract data
		photon_arrival_times = run.get_result_array(group='extract_photon_arrival_times',name='processed_arrivals_ch_1')

		#check to see if we need to run empty cavity analysis
		for each_key in cavity_scan_parameters.keys():
			if each_key == 'empty_cavity':
				empty_cavity_analysis(
					data=photon_arrival_times,
					scan_parameters=cavity_scan_parameters[each_key],
					path=path
				)
	except:
		print("Error: Could not extract cavity_scan_parameters or photon_arrival_times?")
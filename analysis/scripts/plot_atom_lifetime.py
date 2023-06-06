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

def get_results(run):
	i = 1
	NO_ERROR = True
	results = []
	times   = []
	x = np.nan
	y = np.nan
	while NO_ERROR:
		try:
			y =	run.get_result('neta_variance_estimator',f'std_dev_{i}')
			x =	run.get_result('neta_variance_estimator',f'start_time_{i}')
			NO_ERROR = True
			i += 1
		except:
			NO_ERROR= False
		results.append(y)
		times.append(x)
	return results,times


def main():
	run = Run(path)
	results,times = get_results(run)
	plt.semilogy(times,np.square(results))
	plt.ylabel("neta_variance_estimator")
	plt.xlabel("Time (s)")
	plt.ylim(bottom=0)
if __name__ == '__main__':
	main()

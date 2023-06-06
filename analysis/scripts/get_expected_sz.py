from lyse import path, Run

import numpy as np
from numpy import array
import matplotlib.pyplot as plt
from math import pi
from scipy.optimize import curve_fit
from uncertainties import ufloat, nominal_value, std_dev
from labscriptlib.ybclock.analysis.functions import drop_nans_and_infs
import traceback
import sys
def calculate_sz(unitary):
	try:
		unitary = np.matrix(unitary)
		Sz = -np.matrix([[1,0],[0,-1]])
		Sz_of_t = unitary.getH() @ Sz @ unitary

		mean_sz = np.diag(Sz_of_t)[1] #get the second component as its the spin down mean.
		return np.real(mean_sz)
	except:
		return np.nan

def calculate_sz_std_dev(unitary):
	try:
		unitary = np.matrix(unitary)
		Sz = -np.matrix([[1,0],[0,-1]])
		Sz_of_t = unitary.getH() @ Sz @ unitary

		sz_squared = np.diag(Sz_of_t @ Sz_of_t)[1] #get the second component as its the spin down mean.
		variance = np.real(sz_squared) - calculate_sz(unitary)**2
		std_dev = np.sqrt(variance)
		return std_dev
	except:
		# traceback.print_exception(*sys.exc_info())
		return np.nan


def get_expected_sz(run):
	from labscriptlib.ybclock.classes import ExperimentalCavity
	sz = []
	exp_cavity = ExperimentalCavity()
	cavity_scan_parameters = exp_cavity.get_parameters(path)
	atom_scans = cavity_scan_parameters['atoms_in_cavity']
	unitarys = [ atom_scan['unitary'] for atom_scan in atom_scans]

	mean_sz = [calculate_sz(U) for U in unitarys]
	std_sz	= [calculate_sz_std_dev(U) for U in unitarys]
	return mean_sz, std_sz

def main():
	run = Run(path)
	mean_sz, std_sz = get_expected_sz(run)
	N = len(mean_sz)
	print(mean_sz)
	print(std_sz)
	for i in range(N):
		run.save_result(name=f'mean_sz_{i+1}', value=mean_sz[i])
		run.save_result(name=f'std_sz_{i+1}', value=std_sz[i])
if __name__ == '__main__':
	main()
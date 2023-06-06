from lyse import *
import numpy as np
from numpy import array
import matplotlib.pyplot as plt
from math import pi
from scipy.optimize import curve_fit
from uncertainties import ufloat, nominal_value, std_dev
from labscriptlib.ybclock.analysis.functions import drop_nans_and_infs
def ramsey_oscillation_fun(x, contrast=0, offset=0, phi=0):
	return -np.abs(contrast)*np.cos(x + phi) + offset

DEBUG = False

def fit_ramsey_oscillation(xdata, ydata, guess=[0,0,0]):
	parameters, covariance = curve_fit(ramsey_oscillation_fun, xdata,ydata, p0=guess)
	contrast	= parameters[0]
	offset  	= parameters[1]
	try:
		phase	= parameters[2]
	except:
		phase = 0

	perr = np.sqrt(np.diag(covariance))

	contrast_err	= perr[0]
	offset_err  	= perr[1]
	try:
		phase_err	= perr[2]
	except:
		phase_err = 0

	contrast	= ufloat(contrast, contrast_err)
	phase   	= ufloat(phase,phase_err)
	offset  	= ufloat(offset,offset_err)
	return contrast, offset, phase

def get_result(*args):
	return array(df[args])

def calculate_sz(unitary):
	unitary = np.matrix(unitary)
	Sz = 1/2*np.matrix([[1,0],[0,-1]])
	Sz_of_t = unitary.getH() @ Sz @ unitary

	mean_sz = np.diag(Sz_of_t)[1] #get the second component as its the spin down mean.
	return np.real(mean_sz)

def calculate_sz_std_dev(unitary):
	unitary = np.matrix(unitary)
	Sz = 1/2*np.matrix([[1,0],[0,-1]])
	Sz_of_t = unitary.getH() @ Sz @ unitary

	sz_squared = np.diag(Sz_of_t @ Sz_of_t)[1] #get the second component as its the spin down mean.
	variance = np.real(sz_squared) - calculate_sz(unitary)**2
	std_dev = np.sqrt(std_dev)
	return std_dev


def get_expected_sz_curve(df,parameter_str,which_scan):
	from labscriptlib.ybclock.classes import ExperimentalCavity
	times = []
	sz = []
	filepaths = list(df['filepath'])
	for path in filepaths:
		run = Run(path)
		exp_cavity = ExperimentalCavity()
		cavity_scan_parameters = exp_cavity.get_parameters(path)
		atom_scans = cavity_scan_parameters['atoms_in_cavity']
		atom_scan = atom_scans[which_scan - 1]
		unitary = atom_scan['unitary']
		if unitary is None:
			continue
		else:
			sz.append(calculate_sz(unitary))
			times.append(df[df['filepath'] == path][parameter_str])
	return times, np.array(sz)
def post_select_parameter_in_range(df, key, _min,_max):
	a = df[key]
	c1 = a >= _min
	c2 = a <= _max
	c3 = c1 & c2
	return df[c3]
def post_select_atom_number_in_range(df, keys, _min,_max):
	a = 0
	for key in keys:
		a += df[key]
	c1 = a >= _min
	c2 = a <= _max
	c3 = c1 & c2
	return df[c3]

if __name__ == '__main__':
	try:
		df = data(n_sequences=17)
		df = data()

		#filter by sequence
		sequence_name = 'spin_phase_shift_per_squeezing_photon_in_a_1D_trap.py'
		filter_index = df['labscript'] == sequence_name
		df = df[filter_index]

		#filter by photon number
		df = post_select_parameter_in_range(df, ('cavity_photon_count_analysis', 'squeezing_photons_0'), _min=0, _max=1000)
		df = post_select_parameter_in_range(df, ('squeezing_pulse_duration'), _min=9.9, _max=10.1)
		df = post_select_atom_number_in_range(df,
			[('cavity_scan_analysis', 'Neta_3'),('cavity_scan_analysis', 'Neta_4')]
			, _min=1700, _max=2300)

		avg_photon = np.nanmean(df['cavity_photon_count_analysis','squeezing_photons_0'])
		std_photon = np.nanstd(df['cavity_photon_count_analysis','squeezing_photons_0'])
		if DEBUG : print(len(df))

		parameter_str = 'phase_shift_ramsey_phase'
		t_exp, sz_exp = get_expected_sz_curve(df,parameter_str,which_scan=4)
		Neta_up  	= array(df['cavity_scan_analysis','Neta_3'])
		Neta_down	= array(df['cavity_scan_analysis','Neta_4'])
		larmor_detuning = np.nanmean(array(df['rf_larmor_detuning']))/1e3
		Neta_tot  	= Neta_down + Neta_up
		delta_Neta	= Neta_up - Neta_down
		sz        	= delta_Neta/Neta_tot
		parameter 	= array(df[parameter_str])
		plt.scatter(t_exp,sz_exp/(1/2),label=r'Expected $S_z/S$',marker='*',s=200)

		parameter, sz = drop_nans_and_infs(parameter, sz)
		#plot data
		scale_data = np.nanstd(sz)/np.nanstd(sz_exp)
		# plt.scatter(t_exp,sz_exp*scale_data,label=r'Contrast Scaled Expected $S_z/S$',marker='*',s=200)		
		try:
			plt.scatter(parameter,sz,label=r'$S_z/S$')		
		except:
			import traceback
			import sys
			traceback.print_exception(*sys.exc_info())
		plt.legend()
		t = np.linspace(np.min(parameter), np.max(parameter),1000)
		#fit data
		guess = [0.5, 0,0]
		try:
			contrast,offset, phase = fit_ramsey_oscillation(parameter,sz,guess)
			plt.plot(
				t, 
				ramsey_oscillation_fun(t,nominal_value(contrast),nominal_value(offset),nominal_value(phase)),
				label=f'Fit:\nContrast=${np.abs(contrast):L}$,\n$\\phi$=${phase:L}$\nOffset=${offset:L}$'
				)
		except:
			print("Fit Failed")
			import traceback
			import sys
			traceback.print_exception(*sys.exc_info())
		plt.legend()
		plt.ylabel(r'$S_z/S$')
		plt.xlabel(parameter_str)
		plt.title(f"Avg. Photons = {avg_photon:0.2f}")

		print("Done.")
	except Exception as e:
		import traceback
		import sys
		traceback.print_exception(*sys.exc_info())
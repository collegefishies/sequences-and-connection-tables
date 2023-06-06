from lyse import *
import numpy as np
from numpy import array
import matplotlib.pyplot as plt
from math import pi
from scipy.optimize import curve_fit
from labscriptlib.ybclock.analysis.functions import drop_nans_and_infs
from uncertainties import ufloat, nominal_value, std_dev
import pandas as pd
# from labscriptlib.ybclock.analysis.scripts.meta.calibrate_phase_shift_per_photon import post_select_atom_number_in_range,post_select_parameter_in_range

def post_select_atom_number_in_range(df, keys, _min,_max):
	a = 0
	for key in keys:
		a += df[key]
	c1 = a >= _min
	c2 = a <= _max
	c3 = c1 & c2
	return df[c3]

def rabi_flop_func(t, contrast=0, frequency=0, offset=0, phi=0,alpha=0):
	return -np.abs(contrast)*np.cos(2*pi*frequency*t + phi)*np.exp(-np.abs(alpha)*t) + offset
def fit_rabi_flop(xdata, ydata, guess=[0,0,0]):
	parameters, covariance = curve_fit(rabi_flop_func, xdata,ydata, p0=guess)
	contrast 	= parameters[0]
	frequency	= parameters[1]
	offset   	= parameters[2]
	try:
		phase	= parameters[3]
	except:
		phase = 0
	try:
		alpha	= parameters[4]
	except:
		alpha = 0
	perr = np.sqrt(np.diag(covariance))

	contrast_err	= perr[0]
	freq_err    	= perr[1]
	offset_err  	= perr[2]
	try:
		phase_err	= perr[3]
	except:
		phase_err = 0
	try:
		alpha_err	= perr[3]
	except:
	    alpha_err = 0
	contrast 	= ufloat(contrast, contrast_err)
	frequency	= ufloat(frequency, freq_err)
	phase    	= ufloat(phase,phase_err)
	offset   	= ufloat(offset,offset_err)
	alpha    	= ufloat(alpha,alpha_err)
	return contrast, frequency, offset, phase, alpha

def get_result(*args):
	return array(df[args])

def calculate_sz(unitary):
	unitary = np.matrix(unitary)
	# print(unitary)
	Sz = np.matrix([[1,0],[0,-1]])
	Sz_of_t = unitary.getH() @ Sz @ unitary

	mean_sz = np.diag(Sz_of_t)[1] #get the second component as its the spin down mean.
	return np.real(mean_sz)

def calculate_sz_std_dev(unitary):
	unitary = np.matrix(unitary)
	Sz = np.matrix([[1,0],[0,-1]])
	Sz_of_t = unitary.getH() @ Sz @ unitary
	rho = unitary.getH() @ np.matrix([[0,0],[0,1]])  @ unitary
	probability = np.real(np.trace(rho))
	# sz_squared = np.diag(Sz_of_t @ Sz_of_t)[1] #get the second component as its the spin down mean.
	# variance = np.real(sz_squared) - calculate_sz(unitary)**2
	# std_dev = np.sqrt(variance)
	return np.abs((1-probability)/4)


def get_expected_sz_curve(df,parameter_str,which_scan):
	from labscriptlib.ybclock.classes import ExperimentalCavity
	times = []
	sz = []
	sz_dev = []
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
			sz_dev.append(calculate_sz_std_dev(unitary))
			particular_run = df[df['filepath'] == path]
			x = float(particular_run[parameter_str])
			times.append(x)
	return times, np.array(sz), np.array(sz_dev)

if __name__ == '__main__':
	try:
		df = data()

		#filter by sequence
		sequence_name 	= 'calibrate_rabi_flop.py'
		filter_index  	= df['labscript'] == sequence_name
		sequence_name 	= 'calibrate_rabi_flop_low_freq.py'
		o_filter_index	= df['labscript'] == sequence_name
		df1 = df[filter_index]
		df2 = df[o_filter_index]
		df = pd.concat([df1,df2])
		if len(df) < 1:
			raise "Error: len(df) == 0"

		#filter by atom number
		# df = post_select_atom_number_in_range(df,[('cavity_scan_analysis','Neta_3'),('cavity_scan_analysis','Neta_4')],_min=1700,_max=2400)
		
		parameter_str = 'calibration_rabi_pulse_duration'
		t_exp, sz_exp, sz_dev = get_expected_sz_curve(df,parameter_str,which_scan=4)

		FILTER_BY_TIME = False
		if FILTER_BY_TIME:
			pass

		parameter_str = 'calibration_rabi_pulse_duration'
		Neta_up   	= array(df['cavity_scan_analysis','Neta_3'])
		Neta_down 	= array(df['cavity_scan_analysis','Neta_4'])
		Neta_tot  	= Neta_down + Neta_up
		delta_Neta	= Neta_up - Neta_down
		sz        	= delta_Neta/Neta_tot
		parameter 	= array(df[parameter_str])
		photons = array(df['cavity_scan_analysis', 'number_of_detected_photons_1'])
		plt.errorbar(parameter,sz_exp, yerr=sz_dev, label=r'Expected $S_z/S$', marker='*',linestyle='',alpha=0.3)		
		parameter, sz = drop_nans_and_infs(parameter, sz)
		#plot data
		plt.scatter(parameter,sz,s=10,label=r'$S_z/S$')		

		t = np.linspace(np.min(parameter), np.max(parameter),1000)
		#fit data
		guess = [0.8, 1/4.5,0,0]
		# guess = [0.8, 0.020,0,0,0.01]
		contrast, frequency,offset, phase, alpha = fit_rabi_flop(parameter,sz,guess)
		plt.plot(
			t, 
			rabi_flop_func(
				t,
				nominal_value(contrast),
				nominal_value(frequency),
				nominal_value(offset),
				nominal_value(phase),
				nominal_value(alpha)
			),
			label=f'Fit:\nContrast=${contrast:L}$,\nRF Rabi frequency=${frequency*1000:L}$ Hz\n$\\phi$=${phase:L}$\nOffset=${offset:L}$\n$\\alpha={alpha:L}$'
			)
		plt.legend()
		plt.ylabel(r'$S_z/S$')
		plt.xlabel(parameter_str)
		plt.title(f"Scan Photons: ${ufloat(np.nanmean(photons), np.nanstd(photons)):.3L}$\nPhoton Variance Ratio: {np.nanvar(photons)/np.nanmean(photons):.3f}")
		print("Done.")
	except Exception as e:
		import traceback
		import sys
		traceback.print_exception(*sys.exc_info())
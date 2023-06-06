from lyse import *
import numpy as np
from numpy import array
import matplotlib.pyplot as plt
from math import pi
from scipy.optimize import curve_fit
from uncertainties import ufloat, nominal_value, std_dev
from labscriptlib.ybclock.analysis.functions import drop_nans_and_infs
def larmor_oscillation_func(t, contrast=0, frequency=0, offset=0, phi=0):
	return contrast/2*np.cos(2*pi*frequency*t + phi) + offset

def fit_larmor_oscillation(xdata, ydata, guess=[0,0,0]):
	parameters, covariance = curve_fit(larmor_oscillation_func, xdata,ydata, p0=guess)
	contrast 	= parameters[0]
	frequency	= parameters[1]
	offset   	= parameters[2]
	try:
		phase	= parameters[3]
	except:
		phase = 0

	perr = np.sqrt(np.diag(covariance))

	contrast_err	= perr[0]
	freq_err    	= perr[1]
	offset_err  	= perr[2]
	try:
		phase_err	= perr[3]
	except:
		phase_err = 0

	contrast 	= ufloat(contrast, contrast_err)
	frequency	= ufloat(frequency, freq_err)
	phase    	= ufloat(phase,phase_err)
	offset   	= ufloat(offset,offset_err)
	return contrast, frequency, offset, phase

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
if __name__ == '__main__':
	try:
		df = data(n_sequences=17)
		df = data()

		#filter by sequence
		sequence_name = 'calibrate_larmor_frequency.py'
		filter_index = df['labscript'] == sequence_name
		df = df[filter_index]

		parameter_str = 'ramsey_phase'
		parameter_str = 'calibration_precession_time'
		t_exp, sz_exp = get_expected_sz_curve(df,parameter_str,which_scan=4)
		Neta_up  	= array(df['cavity_scan_analysis','Neta_3'])
		Neta_down	= array(df['cavity_scan_analysis','Neta_4'])
		larmor_detuning = np.nanmean(array(df['rf_larmor_detuning']))/1e3
		Neta_tot  	= Neta_down + Neta_up
		delta_Neta	= Neta_up - Neta_down
		sz        	= delta_Neta/Neta_tot/2
		parameter 	= array(df[parameter_str])
		photons = array(df['cavity_scan_analysis', 'number_of_detected_photons_1'])
		plt.scatter(t_exp,sz_exp,label=r'Expected $S_z/S$',marker='*',s=200)

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
		guess = [0.5, larmor_detuning, 0,0]
		try:
			contrast, frequency,offset, phase = fit_larmor_oscillation(parameter,sz,guess)
			plt.plot(
				t, 
				larmor_oscillation_func(t,nominal_value(contrast),nominal_value(frequency),nominal_value(offset),nominal_value(phase)),
				label=f'Fit:\nContrast=${contrast:L}$,\nLarmor Correction Needed=${-frequency*1000 + larmor_detuning*1e3:L}$ Hz\n$\\phi$=${phase:L}$\nOffset=${offset:L}$'
				)
		except:
			print("Fit Failed")
			import traceback
			import sys
			traceback.print_exception(*sys.exc_info())
		plt.legend()
		plt.ylabel(r'$S_z/S$')
		plt.xlabel(parameter_str)
		plt.title(f"Scan Photons: ${ufloat(np.nanmean(photons), np.nanstd(photons)):.3L}$\nPhoton Variance Ratio: {np.nanvar(photons)/np.nanmean(photons):.3f}")
		print("Done.")
	except Exception as e:
		import traceback
		import sys
		traceback.print_exception(*sys.exc_info())
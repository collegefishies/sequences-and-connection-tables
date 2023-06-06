from lyse import *
import numpy as np
from numpy import array
import matplotlib.pyplot as plt
import pandas as pd
from sklearn import gaussian_process
from sklearn.gaussian_process.kernels import Matern, WhiteKernel, ConstantKernel

def filter_data(df,atom_number,range):
	boolean = atom_number < range[1]
	boolean2 = atom_number > range[0]
	boolean3 = boolean & boolean2
	return df[boolean3]

def get_rf_rabi_flopping_calibration_parameters():
	sz_over_s = array(df['measure_sz_over_s','sz_over_s'])
	parameter = array(df['rabi_pulse_duration'])
	return parameter, sz_over_s

def get_larmor_flopping_calibration_parameters():
	sz_over_s = array(df['measure_sz_over_s','sz_over_s'])
	parameter = array(df['calibration_precession_time'])
	x_label = 'calibration_precession_time'
	return parameter, sz_over_s, x_label
	
def get_spin_pumping_parameters():
	sz_over_s = array(df['measure_sz_over_s','pumping_fraction'])
	parameter = array(df['y_bias_field_in_cavity'])
	x_label = 'y_bias_field_in_cavity'
	return parameter, sz_over_s, x_label

def get_squeezing_parameters():
	N3 = df['cavity_scan_analysis','Neta_3'].astype(float).values
	N4 = df['cavity_scan_analysis','Neta_4'].astype(float).values
	p1 = df['cavity_photon_count_analysis','squeezing_photons_0'].astype(int).values
	p2 = df['cavity_photon_count_analysis','squeezing_photons_1'].astype(int).values
	Neta = N3 + N4
	photons = p1 + p2
	x_label = 'Neta3+4',
	y_label = 'squeezing photons'
	return Neta, photons, x_label, y_label

if __name__ == '__main__':
	try:
		df = data()

		# x,y = get_rf_rabi_flopping_calibration_parameters()
		x,y,x_label = get_larmor_flopping_calibration_parameters()
		x,y,x_label = get_spin_pumping_parameters()
		x,y,x_label, y_label = get_squeezing_parameters()
		
		plt.scatter(x,y,s=10)	
		plt.legend()
		plt.ylabel(y_label)
		plt.xlabel(x_label)

		print("Done.")
	except Exception as e:
		import traceback
		import sys
		traceback.print_exception(*sys.exc_info())
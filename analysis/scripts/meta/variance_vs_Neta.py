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
def find_number_of_cavity_scans(df):
	count = 0
	no_bug = True
	while no_bug:
		try:
			Neta = array(df['cavity_scan_analys'])
			
		except:
			no_bug = False
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
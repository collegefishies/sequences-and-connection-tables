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
def get_four_points(df):
	N3 = np.array(df['cavity_scan_analysis', 'Neta_3'])
	N4 = np.array(df['cavity_scan_analysis', 'Neta_4'])
	N5 = np.array(df['cavity_scan_analysis', 'Neta_5'])
	N6 = np.array(df['cavity_scan_analysis', 'Neta_6'])
	Neta = (N3 + N4 + N5 + N6)/2
	N3 /= Neta
	N4 /= Neta
	N5 /= Neta
	N6 /= Neta
	return list(zip(N3, N4, N5, N6))
if __name__ == '__main__':
	try:
		df = data()

		for pts in get_four_points(df):
			plt.scatter(
					x=[1,2,3,4],
					y=pts,
					alpha=0.01,
					c = 'tab:blue'
				)
		pts = get_four_points(df)
		pt = pts[-1]
		print(pt)
		plt.scatter(
				x = [1,2,3,4],
				y = pt,
				c = 'k',
				edgecolors='w'
			)

		print("Done.")
	except Exception as e:
		import traceback
		import sys
		traceback.print_exception(*sys.exc_info())
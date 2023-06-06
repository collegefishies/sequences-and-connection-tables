from lyse import *
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from uncertainties import ufloat
def post_select_photon_number(df, photon_number, photon_number_range):
	boolean1 = df['squeezing_photons'] < photon_number	 + photon_number_range/2
	boolean2 = df['squeezing_photons'] > photon_number	 - photon_number_range/2
	boolean = boolean1 & boolean2
	return df[boolean]
def post_select_squeezing_light_power(df, voltage):
	boolean1 = df['squeezing_light_power'] < voltage	 + 0.01
	boolean2 = df['squeezing_light_power'] > voltage	 - 0.01
	boolean = boolean1 & boolean2
	return df[boolean]
def main():
	df = data(n_sequences=100)
	df = data()
	df = post_select_squeezing_light_power(df, voltage=1.3)
	s1 = array(df['cavity_photon_count_analysis','squeezing_photons_0'])
	s2 = array(df['cavity_photon_count_analysis','squeezing_photons_1'])
	print("Post Selecting Over Squeezing Light Power")
	try:
		squeezing_photons = s1 + s2
		df['squeezing_photons'] = squeezing_photons
		imbalance = s1-s2
		bin_width = 1
		bins	= int(np.nanmax(imbalance)-np.nanmin(imbalance))
		plt.hist(imbalance-0.5,bins=bins)
		plt.title(f'Squeezing Photon Imbalance Distribution (s1 - s2)\nAvg Photons: ${ufloat(np.nanmean(squeezing_photons), np.nanstd(squeezing_photons)):L}$\n Avg Imbalance: ${ufloat(np.nanmean(imbalance), np.nanstd(imbalance)):L}$')
		rangep = (np.nanmax(squeezing_photons)-np.nanmin(squeezing_photons))
		plt.xlim([-rangep, +rangep])
		plt.xlabel('Photon Difference')
		plt.ylabel(f'Counts (cts={len(df)})')
		# plt.gca().set_xlim(left=bin_width)
		# plt.gca().set_ylim(top=20)
		print("Done")
	except:
		#Failed, post selection?
		print("Failed. Check Post Selection?")
	pass
if __name__ == '__main__':
	try:
		main()	
	except:
		import traceback
		import sys
		traceback.print_exception(*sys.exc_info())
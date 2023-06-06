from lyse import *
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
from uncertainties import ufloat

eta = ufloat(3.2,0.2)
pi = 3.14159

def post_select_atom_number_in_range(df, keys, _min,_max):
	a = 0
	for key in keys:
		a += df[key]
	c1 = a >= _min
	c2 = a <= _max
	c3 = c1 & c2
	return df[c3]

def gaussian(x,mean, sigma, a):
	root = np.exp(1/2)
	return a*root**(-(x-mean)**2/sigma**2)
def to_ufloat(x,u_x):
	ufloats = []
	for i,u in zip(x,u_x):
		ufloats.append(ufloat(i,u))
	return ufloats
def main():
	# df = data(n_sequences=100)
	df = data()

	#post select on squeezing, or squeezing_unsqueezing scripts
	sequence_names = df['labscript']
	#postselect df using only sequences with 'unsqueezing' in the name
	df = sequence_names.str.contains('unsqueezing')
	print("Postselected on unsqueezing")


	

	title_str = ''
	print("Post Selecting Over Atom Number")
	_min = 1800
	_max = 2200
	df = post_select_atom_number_in_range(
		df, 
		keys=[
			('cavity_scan_analysis', 'Neta_3'),
			('cavity_scan_analysis','Neta_4')
		], 
		_min=_min,
		_max=_max
	)

	#add our postselection criteria to the title with f strings
	title_str += f"\nPS Over Atom Number {_min} to {_max}"


	desired_angle = pi/2
	print(f"Post Select on Angle {desired_angle}")
	df = post_select_atom_number_in_range(
		df,
		keys = [('final_angle_alpha',)],
		_min=desired_angle-0.01,
		_max=desired_angle+0.01,
		)
	title_str += f"\nPS Over Angle {desired_angle}"


	WANT_SQUEEZING_DATA = True
	POST_SELECT_LIGHT_POWER = True
	if POST_SELECT_LIGHT_POWER:
		if WANT_SQUEEZING_DATA:
			voltage = 1.3
			print(f"Post Selecting over squeezing_light_voltage {voltage}")
			df = post_select_atom_number_in_range(
				df, 
				keys=[
					('squeezing_light_power',)
				], 
				_min=voltage - 0.01,
				_max=voltage + 0.01
			)
			title_str += f"\nPS Over Squeezing Light Voltage {voltage}"
		else:
			voltage = 0
			df = post_select_atom_number_in_range(
				df, 
				keys=[
					('SQUEEZING',)
				], 
				_min=voltage - 0.01,
				_max=voltage + 0.01
			)
			#mention that there is no squeezing light
			title_str += f"\nPS No Squeezing Light"
	else:
		#no post selection
		title_str += f"\nNo Post Selection vs. Squeezing Light"
		voltage = np.nan



	print("Calculating Sz, Neta Qtys")
	try:
		Neta_3 = array(df['cavity_scan_analysis','Neta_3'])
		Neta_4 = array(df['cavity_scan_analysis','Neta_4'])
		Neta_total = Neta_3 + Neta_4
		sz = (Neta_3 - Neta_4)/Neta_total
		Ntotal_avg = np.nanmean(Neta_total)
		df['Neta_total'] = Neta_total
	except:
		print("Error: Could not calculate Neta_total")
		sz = np.nan
		Ntotal_avg = np.nan
		Neta_total = np.nan
		df['Neta_total'] = np.nan
	
	try:
		#plot histogram
		bins	= 10
		bin_width = np.max(Neta_total)/bins
		counts, bins, patches = plt.hist(sz,bins=bins)
	except:
		print("Error: Could not plot histogram")
	try:
		#fit histogram
		params, covariance = curve_fit(gaussian, (bins[:-1]+bins[1:])/2, counts, p0=[np.nanmean(sz),np.nanstd(sz),np.max(counts)])
		#plot fit
		x = np.linspace(bins[0],bins[-1],1000)
		print(params.shape)
		perr = np.sqrt(np.diag(covariance))
		u_params = to_ufloat(params, perr)
		plt.plot(x, gaussian(x,*params), label=f"Fit: $\\mu = {u_params[0]:L}$\n$\\sigma = {u_params[1]:L}$\n$\\sigma^2/\\sigma^2_{{SQL}} = {Ntotal_avg/eta*u_params[1]**2:L}$")
	except:
		print("Error: Could not fit histogram")
		params = np.nan*np.ones(3)
		perr = np.nan*np.ones(3)
		u_params = to_ufloat(params, perr)
		#calculate the mean and std of the sz






	try:
		sz_mean = np.nanmean(sz)
		sz_std = np.nanstd(sz)
	except:
		sz_mean = np.nan
		sz_std = np.nan
	#add the mean and std to the title
	title_str += f"\nMean Sz: {sz_mean:3f}\nStd Sz: {sz_std:3f}"
	plt.xlim([-1,1])
	# plt.plot(bins[:-1],counts)
	# mlab.normpdf(bins, mu,sigma)
	# final_angle_alpha = float(df['final_angle_alpha'][-1])
	final_angle_alpha = desired_angle
	plt.title(f'Sz Distribution ($\\Delta N/(2N)$)\n $\\alpha = {final_angle_alpha:.3f}$\n voltage = {voltage} V' + title_str)
	plt.xlabel('sz/s')
	plt.ylabel(f'Counts (cts={len(df)})')
	plt.legend()
	# plt.gca().set_xlim(left=bin_width)
	# plt.gca().set_ylim(top=20)
	print("Done")
	pass
if __name__ == '__main__':
	try:
		main()	
	except:
		import traceback
		import sys
		traceback.print_exception(*sys.exc_info())

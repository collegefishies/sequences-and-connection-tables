from lyse import *
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
from uncertainties import ufloat

eta = 3.2

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
	df = post_select_atom_number_in_range(
		df, 
		keys=[
			('cavity_scan_analysis', 'Neta_3'),
			('cavity_scan_analysis','Neta_4')
		], 
		_min=1600,
		_max=2400
	)
	df = post_select_atom_number_in_range(
		df, 
		keys=[
			('cavity_photon_count_analysis', 'squeezing_photons_0'),
			('cavity_photon_count_analysis','squeezing_photons_1')
		], 
		_min=0,
		_max=13
	)
	Neta_3 = array(df['cavity_scan_analysis','Neta_3'])
	Neta_4 = array(df['cavity_scan_analysis','Neta_4'])
	Neta_total = Neta_3 + Neta_4
	sz = (Neta_3 - Neta_4)/Neta_total/2
	Ntotal_avg = np.mean(Neta_total)
	df['Neta_total'] = Neta_total

	#plot histogram
	bins	= 10
	bin_width = np.max(Neta_total)/bins
	counts, bins, patches = plt.hist(sz,bins=bins)

	#fit histogram
	params, covariance = curve_fit(gaussian, (bins[:-1]+bins[1:])/2, counts, p0=[0.1,0.1,1])
	#plot fit
	x = np.linspace(bins[0],bins[-1],1000)
	print(params.shape)
	perr = np.sqrt(np.diag(covariance))
	u_params = to_ufloat(params, perr)
	plt.plot(x, gaussian(x,*params), label=f"Fit: $\\mu = {u_params[0]:L}$\n$\\sigma = {u_params[1]:L}$\n$\\sigma^2 = {4*Ntotal_avg/eta*u_params[1]**2:L}$")
	plt.xlim([-0.5,0.5])
	# plt.plot(bins[:-1],counts)
	# mlab.normpdf(bins, mu,sigma)
	final_angle_alpha = float(df['final_angle_alpha'][-1])
	plt.title(f'Sz Distribution ($\\Delta N/(2N)$)\n $\\alpha = {final_angle_alpha:.3f}$')
	plt.xlabel('sz')
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

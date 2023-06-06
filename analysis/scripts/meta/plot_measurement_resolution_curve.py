from lyse import *
import numpy as np
from numpy import array
import matplotlib.pyplot as plt
import pandas as pd

'''
This code must be commented
'''

analyze_guessed_Neta = True

def filter_data(df,atom_number,range):
	boolean = atom_number < range[1]
	boolean2 = atom_number > range[0]
	boolean3 = boolean & boolean2
	return df[boolean3]

def return_data(df):
	#get neta data
	N3 = np.array(df['cavity_scan_analysis', 'Neta_3'])
	N4 = np.array(df['cavity_scan_analysis', 'Neta_4'])
	N5 = np.array(df['cavity_scan_analysis', 'Neta_5'])
	N6 = np.array(df['cavity_scan_analysis', 'Neta_6'])
	Neta = (N3 + N4 + N5 + N6)/2
	N3 /= Neta
	N4 /= Neta
	N5 /= Neta
	N6 /= Neta

	#get photon data
	p3 = np.array(df['cavity_scan_analysis', 'number_of_detected_photons_3'])
	p4 = np.array(df['cavity_scan_analysis', 'number_of_detected_photons_4'])
	p5 = np.array(df['cavity_scan_analysis', 'number_of_detected_photons_5'])
	p6 = np.array(df['cavity_scan_analysis', 'number_of_detected_photons_6'])
	photon_data = np.stack((p3,p4,p5,p6), axis=-1)

	#calculate photons with uncertainty
	photons = np.nanmean(photon_data, axis=-1)
	uncertainty = np.nanstd(photon_data, axis=-1)
	from uncertainties import unumpy
	photons = unumpy.uarray(photons, uncertainty)

	#calculate spin variance with uncertainty
	Sz1 = N3-N4
	Sz2 = N6-N5
	deltaSz = Sz1-Sz2

def return_data_guess(df):
	#get neta data from the Neta_guess (before fit)
	
	N3 = np.array(df['cavity_scan_analysis', 'Neta_guess_3'])
	N4 = np.array(df['cavity_scan_analysis', 'Neta_guess_4'])
	N5 = np.array(df['cavity_scan_analysis', 'Neta_guess_5'])
	N6 = np.array(df['cavity_scan_analysis', 'Neta_guess_6'])

	Neta = (N3 + N4 + N5 + N6)/2
	N3 /= Neta
	N4 /= Neta
	N5 /= Neta
	N6 /= Neta

	#get photon data
	p3 = np.array(df['cavity_scan_analysis', 'number_of_detected_photons_3'])
	p4 = np.array(df['cavity_scan_analysis', 'number_of_detected_photons_4'])
	p5 = np.array(df['cavity_scan_analysis', 'number_of_detected_photons_5'])
	p6 = np.array(df['cavity_scan_analysis', 'number_of_detected_photons_6'])
	photon_data = np.stack((p3,p4,p5,p6), axis=-1)

	#calculate photons with uncertainty
	photons = np.nanmean(photon_data, axis=-1)
	uncertainty = np.nanstd(photon_data, axis=-1)
	from uncertainties import unumpy
	photons = unumpy.uarray(photons, uncertainty)

	#calculate spin variance with uncertainty
	Sz1 = N3-N4
	Sz2 = N6-N5
	deltaSz = Sz1-Sz2
	
	return deltaSz, photons

def return_data_spin_up(df):
	#get neta data
	N3 = np.array(df['cavity_scan_analysis', 'Neta_3'])
	N4 = np.array(df['cavity_scan_analysis', 'Neta_4'])
	N5 = np.array(df['cavity_scan_analysis', 'Neta_5'])
	N6 = np.array(df['cavity_scan_analysis', 'Neta_6'])

	N = (N3 + N4 + N5 + N6)/4
	#get photon data
	p3 = np.array(df['cavity_scan_analysis', 'number_of_detected_photons_3'])
	p4 = np.array(df['cavity_scan_analysis', 'number_of_detected_photons_4'])
	p5 = np.array(df['cavity_scan_analysis', 'number_of_detected_photons_5'])
	p6 = np.array(df['cavity_scan_analysis', 'number_of_detected_photons_6'])
	photon_data = np.stack((p3,p4,p5,p6), axis=-1)

	#calculate photons with uncertainty
	photons = np.nanmean(photon_data, axis=-1)
	uncertainty = np.nanstd(photon_data, axis=-1)
	from uncertainties import unumpy
	photons = unumpy.uarray(photons, uncertainty)
	
	return (N3 - N4)/2, photons, N

def return_data_spin_up_guess(df):
	#get neta data
	N3 = np.array(df['cavity_scan_analysis', 'Neta_guess_3'])
	N4 = np.array(df['cavity_scan_analysis', 'Neta_guess_4'])
	N5 = np.array(df['cavity_scan_analysis', 'Neta_guess_5'])
	N6 = np.array(df['cavity_scan_analysis', 'Neta_guess_6'])

	N = (N3 + N4 + N5 + N6)/4
	#get photon data
	p3 = np.array(df['cavity_scan_analysis', 'number_of_detected_photons_3'])
	p4 = np.array(df['cavity_scan_analysis', 'number_of_detected_photons_4'])
	p5 = np.array(df['cavity_scan_analysis', 'number_of_detected_photons_5'])
	p6 = np.array(df['cavity_scan_analysis', 'number_of_detected_photons_6'])
	photon_data = np.stack((p3,p4,p5,p6), axis=-1)

	#calculate photons with uncertainty
	photons = np.nanmean(photon_data, axis=-1)
	uncertainty = np.nanstd(photon_data, axis=-1)
	from uncertainties import unumpy
	photons = unumpy.uarray(photons, uncertainty)
	
	return (N3 - N4)/2, photons, N

def calculateVarianceVsPhotons(deltaSz, photons, photon_bins,N):
	bins = photon_bins
	digitized = np.digitize(photons, bins)

	#calculate variance and error
	deltaSzVariances = np.array([np.nanvar(deltaSz[digitized==i]) for i in range(1,len(bins))])
	import sys
	N_count = np.bincount(digitized) + sys.float_info.epsilon
	# N_count.resize(len(deltaSzVariances))
	N_count.resize(len(bins)-1)
	u_deltaSzVariances = np.where(N_count > 2, np.power(2.0/(N_count - 1),0.5)*deltaSzVariances, np.full(shape=N_count.shape,fill_value=1e9)*deltaSzVariances)

	#wrap in uncertainties objcet
	from uncertainties import unumpy as unp
	deltaSzVariances = unp.uarray(deltaSzVariances, u_deltaSzVariances)

	#calculate photons
	photons = np.array(
		[
			np.mean(
				photons[digitized==i]
			) for i in range(1,len(bins))
		])


	return deltaSzVariances, photons

def unpack(x):
	from uncertainties import unumpy
	u_a = unumpy.std_devs(x)
	a	= unumpy.nominal_values(x)
	return a, u_a

def replace_nan_with_infs(x):
	x[np.isnan(x)] = 1000
	x[np.isinf(x)] = 1000
	return x





if __name__ == '__main__':
	try:
		df = data()
		y, x, N = return_data_spin_up(df)
		photons_measured = x[-1]
		bins = np.logspace(0,4,25)
		y, x = calculateVarianceVsPhotons(
			deltaSz=y, 
			photons=x,
			N=N,
			photon_bins=bins
		)
		from uncertainties import unumpy as unp
		# y, u_y = unpack(10*unp.log(y/10)/unp.log(10))
		y, u_y = unpack(y)
		x, u_x = unpack(x)

		u_y = replace_nan_with_infs(u_y)
		u_x = replace_nan_with_infs(u_x)
		# print(u_y)
		plt.errorbar(
			x[u_y < 1e8],
			y[u_y < 1e8],
			xerr=u_x[u_y < 1e8],
			yerr=u_y[u_y < 1e8],
			fmt='o',
			label = 'fitted Neta'
			)
		# if len(y[u_y < 1e8]) > 2:
		plt.yscale("log")
		plt.xscale("log")
		# plt.ylim([-70,-30])
		plt.ylabel("Var[(Neta_3 - Neta_4)/2]")
		plt.xlabel("Number of Cavity Scan Photons")
		plt.title(f"Measurement quality\nSpin Up")
		
		# Plot here the measurement quality given by initial guess only
		if analyze_guessed_Neta :
			try:
				yg, xg, Ng = return_data_spin_up_guess(df)
				photons_measured = x[-1]
				yg, xg = calculateVarianceVsPhotons(
					deltaSz=yg, 
					photons=xg,
					N=Ng,
					photon_bins=bins
				)
				from uncertainties import unumpy as unp
				# y, u_y = unpack(10*unp.log(y/10)/unp.log(10))
				yg, u_yg = unpack(yg)
				xg, u_xg = unpack(xg)

				u_yg = replace_nan_with_infs(u_yg)
				u_xg = replace_nan_with_infs(u_xg)

				plt.errorbar(
				xg[u_yg < 1e8],
				yg[u_yg < 1e8],
				xerr=u_xg[u_yg < 1e8],
				yerr=u_yg[u_yg < 1e8],
				fmt='s',
				label = 'guessed Neta'
				)

			except Exception as ex:
				print("Failed getting guessed Neta. The reason is : ", e)
		xph = np.logspace(np.log10(20),np.log10(4000))
		yph = 16000/xph+0.06*xph
		plt.plot(
			xph,
			yph,
			label="16000/nph+0.06*nph")
		plt.legend()

	except Exception as e:
		import traceback
		import sys
		traceback.print_exception(*sys.exc_info())
'''
	#Basic Idea
	the variance of (Neta) = mean(N) eta^2.
	the mean of (Neta) = Neta_spin polarized
	So the ratio gives eta.

	But rather than simply taking ratios to line variance vs mean of Neta is
	fitted, with the slope giving eta.

	#Measure with One Shot 

	The polarized atom number measures the total Neta precisely (to within 3
	atoms say). This, with one measurement directly gives Neta with no noise.

	If we measure, either the unpolarized loaded atom number, or the
	projection of the x coherent state along the z axis, this will give a
	sample of a distribution with variance proportional to the total
	number of atoms.

	#Measure many times in one shot

	Just do a for loop, polarize, measure sz component, many times in one shot to measure.
	
	#Analyzing the Data

	Regardless of the technique, one needs to bin the data
	(Neta_polarized, Neta_unpolarized) according to the polarized value,
	to calculate the variance.
'''
from lyse import *
import numpy as np
from numpy import array
import matplotlib.pyplot as plt
from math import pi
from scipy.optimize import curve_fit
from uncertainties import ufloat, nominal_value, std_dev
import time


def canonical_method(df):
	'''
		The first generation ybclock way of calculating eta.
	'''
	Nup1 = array(df['cavity_scan_analysis','Neta_3'])
	Nup2 = array(df['cavity_scan_analysis','Neta_6'])
	Ndown1= array(df['cavity_scan_analysis','Neta_4'])
	Ndown2= array(df['cavity_scan_analysis','Neta_5'])
	SzEta = (Nup1-Ndown1)/2
	SzEta2 = (Nup2-Ndown2)/2
	Neta_total = (Nup1+Nup2+Ndown1+Ndown2)/2
	df['Neta_total'] = Neta_total
	df['SzEta'] = SzEta
	df['SzEta2'] = SzEta2
	# plt.scatter(Neta_total, SzEta, s=10, label='Canonical Sz')
	# plt.plot(Neta_total, 0*Neta_total)
	# plt.ylabel("SzEta")
	# plt.xlabel("Neta_total")

	return df
	pass

def enriques_method(df):
	#unpolarized atom number
	Neta_sample  	= array(df['cavity_scan_analysis','Neta_1'])
	# Neta_sample	= array(df['neta_variance_estimator','std_dev_1'])
	#polarized atom number
	Neta_tot  	= array(df['cavity_scan_analysis','Neta_2'])
	# Neta_tot	= array(df['neta_variance_estimator','std_dev_2'])

	zipped_data = zip(Neta_tot, Neta_sample)

	#plot data
	# plt.scatter(Neta_tot,Neta_sample,s=10,label=r'$Neta$')
	# plt.plot(Neta_tot,Neta_tot/2,label=r'$Neta$')
	# plt.ylabel('Neta_Unpolarized')
	# plt.xlabel('NetaPolarized')

	return Neta_tot, Neta_sample

def bin_data(x,y, bin_width=None,bins=None,min=None,max=None):
	if not min:
		a = np.nanmin(x)
	else:
		a = min
	if not max:
		b = np.nanmax(x)
	else:
		b = max
	if bin_width:
		bins = np.arange(a,b,bin_width)
	elif bins:
		bins = np.linspace(a,b,bins)
	bin_indices = np.digitize(x, bins)

	binned_data = []
	for i in range(len(bins)+1):
		binned_data.append([])
	for bin_index, y in zip(bin_indices,y):
		if not np.isnan(y):
			binned_data[bin_index].append(y)
	return binned_data, bins

def remove_outliers(data, zscoreAccpetance = 3.):
    """
    Calculate modified Z-scores of a set of random data and remove outliers, i.e., data for which the Z-scores>zscoreAcceptance.
    """
    med = np.median(data)
    mad = np.median(np.abs(data - med))
    modZscore = np.abs(0.6725*(data-med)/mad) if mad else 0.
    return data[modZscore<zscoreAccpetance]

def remove_outliers_correlation(data1,data2, zscoreAccpetance = 3.):
    """
    FAILING FOR NOW
    Remove outliers for correlation plot.
    Calculate modified Z-scores of a set of random data and remove outliers, i.e., data for which the Z-scores>zscoreAcceptance.
    """
    med1 = np.median(data1)
    mad1 = np.median(np.abs(data1 - med1))
    modZscore1 = np.abs(0.6725*(data1-med1)/mad1) if mad1 else 0.
    med2 = np.median(data2)
    mad2 = np.median(np.abs(data2 - med2))
    modZscore2 = np.abs(0.6725*(data2-med2)/mad2) if mad2 else 0.
 #   return data1[(modZscore1<zscoreAccpetance)&(modZscore2<zscoreAccpetance)], data2[(modZscore1<zscoreAccpetance)&(modZscore2<zscoreAccpetance)]
    return data1[(modZscore1<zscoreAccpetance)], data2[(modZscore1<zscoreAccpetance)]

def calculate_variance_in_bins(binned_data):
	variance = []
	for dataset in binned_data:
		if len(dataset) > 0:
			# Remove outliers
			dataset = np.array(dataset)
			dataset = remove_outliers(dataset)
			variance_sample = np.nanvar(dataset)
			try:
				error = variance_sample*np.sqrt(2/(len(dataset)-1))
			except ZeroDivisionError as zde:
				error = float('inf')

			variance.append(ufloat(variance_sample, error))
		else:
			variance.append(np.nan)
	return variance

def filter_data(df):
	boolean = df['labscript'] == 'eta_calibration.py'
	dF = df[boolean]
	return df

def line(x,eta):
	return eta*x/4

def fit_line(x,y,guess,err):
	x	= np.array(x)
	y	= np.array(y)
	err = np.array(err)

	x  	= x[~np.isnan(y)]
	err	= err[~np.isnan(y)]
	y  	= y[~np.isnan(y)]

	parameters, covariance = curve_fit(line, x, y , guess, sigma=err, absolute_sigma=True)
	eta = parameters[0]
	perr = np.sqrt(np.diag(covariance))
	slope_err = perr[0]
	eta = ufloat(eta, slope_err)
	return eta

if __name__ == '__main__':
	try:
		df = data()
		print("Filtering Data...")
		df = filter_data(df)
		print(f"\tNumber of Shots: {len(df)}")
		print("Calculating SzEta...")
		df = canonical_method(df)
		x = df['Neta_total']
		y = df['SzEta']
		yp= df['SzEta2']
		y2= df['SzEta']-df['SzEta2']

		print("Binning Data...")
		remove_MeasurementVariance = True #boolean
		plot_MeasurementVariance = False #boolean, 1 will plot measurement resolution vs Neta
		binDef = [7, 500, 5500] #Neta postselecion and binning. Format [bins, min, max] 
		print(f"\tBins: {binDef}")

		binned_data,bins = bin_data(x,y, bins=binDef[0], min=binDef[1], max=binDef[2])
		binned_data2,bins2 = bin_data(x,yp, bins=binDef[0], min=binDef[1], max=binDef[2])
		binned_data_diff,bins_diff = bin_data(x,y2, bins=binDef[0], min=binDef[1], max=binDef[2])

		print("Calculating Variance in Binned Data...")
		variance_SzEta = np.array(calculate_variance_in_bins(binned_data))
		variance_differenceSzEtaSzEta2 = np.array(calculate_variance_in_bins(binned_data_diff))/2

		variance_SzEta = (variance_SzEta - variance_differenceSzEtaSzEta2) if remove_MeasurementVariance else variance_SzEta# subtract measurement resolution from SzEta variance

		nominal_values = []
		errors = []
		print("Compiling errors and values...")
		for var in variance_SzEta:
			nominal_values.append(nominal_value(var))
			errors.append(std_dev(var))

		if plot_MeasurementVariance:
			print("Plotting Data...")
			fig, axs = plt.subplots(3)
			nominal_values_meas = []
			errors_meas = []
			for var in variance_differenceSzEtaSzEta2:
				nominal_values_meas.append(nominal_value(var))
				errors_meas.append(std_dev(var))
			nominal_values_2 = []
			errors_2 = []
			sigmad = fit_line(bins, nominal_values_meas[:-1], guess=[1], err=errors_meas[:-1])
			axs[1].errorbar(bins, nominal_values_meas[:-1],yerr=errors_meas[:-1],label='var($S_z\\eta$)', fmt='o')
			axs[1].plot(bins, line(bins,sigmad.nominal_value), label=f'$\\sigma_d$: ${sigmad:L}$')
			# plt.gca().set_yscale('log')
			# plt.gca().set_xscale('log')
			# plt.ylim([0,20000])
			axs[1].legend()
			axs[1].set_xlabel('$N\\eta$')
			axs[1].set_ylabel('var($S_z1\\eta$-$S_z2\\eta$)')

			for Sz1, Sz2 in zip(binned_data,binned_data2):
				# correlation plot of measurements
				# yl, ylp = remove_outliers_correlation(y,yp) It is Failing
				try:
					axs[2].scatter(Sz1,Sz2,s=10, label='scattered')
				except:
					print("DAMN IT ! Some issue with {len(Sz1)} =/= {len(Sz2)}", len(Sz1) ,len(Sz2))
			axs[2].set_ylim([-300,500])
			axs[2].set_xlim([-300,500])

			axs[2].set_xlabel('$S_z1 \\eta$')
			axs[2].set_ylabel('$S_z2 \\eta$')
			axs[2].set_aspect('equal')
			axs[2].plot([-500+50, 500+50],[-500, 500],color='red')
		else:
			fig, axs = plt.subplots(1)
			axs = [axs]

		print("Fitting data...")
		cut = 10000
		eta = fit_line(bins[:cut], nominal_values[:-1][:cut], guess=[1], err=errors[:-1][:cut])
		axs[0].errorbar(bins, nominal_values[:-1],yerr=errors[:-1],label='var($S_z\\eta$)', fmt='o')
		axs[0].title.set_text(f"$N\\eta \\equiv N\\eta_3 + N\\eta_4$")
		print(nominal_values[:-1][:cut])
		print(eta)
		print("Plotting Fit...")
		axs[0].plot(bins, line(bins,eta.nominal_value), label=f'$\\eta$: ${eta:L}$')
		# plt.gca().set_yscale('log')
		# plt.gca().set_xscale('log')
		# axs[0].plt.ylim([0,20000])
		axs[0].legend()
		axs[0].set_xlabel('$N\\eta$')
		axs[0].set_ylabel('var($S_z\\eta$)')

		print("Done!")
	except Exception as e:
		import traceback
		import sys
		traceback.print_exception(*sys.exc_info())
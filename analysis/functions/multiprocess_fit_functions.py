import numpy as np
import math
from scipy.optimize import minimize, least_squares, differential_evolution, leastsq
from sklearn.cluster import AgglomerativeClustering
import random

import matplotlib.pyplot as plt

DEBUG = False

def square(list):
    return [i ** 2 for i in list]

def lorentzian(x, x0, a, gamma, offset):
	'''
	x    	= position,
	x0   	= peak center,
	a    	= amplitude of peak,
	gamma	= Half width half max, it should be positive!

	'''
	return a/math.pi*abs(gamma)/(gamma**2 + (x-x0)**2) + abs(offset)

def residuals_of_lorentzian(params, x_data, y_data):
	''' Calculates the residuals of the fit.'''
	diff = [lorentzian(x, params[0], params[1], params[2], params[3]) - y for x,y in zip(x_data,y_data)]
	return diff

def fit_single_cavity_peak(data,start,end,bin_interval=0.2):
	''' Fits a single_cavity_peak using least squares. Assumes unbinned photon
	arrival times for data.

	Returns best_guess and cov_best_guess'''

	#bin the data
	(hist, bin_edges) = np.histogram(
		data,
		bins=np.arange(start,end, bin_interval)
	)

	#estimate initial parameters
	amplitude = np.amax(hist)
	x0_index = np.argmax(hist)
	x0 = bin_edges[x0_index]
	locations_greater_than_half_max = np.where(hist > amplitude/2)[0]
	right_time = bin_edges[locations_greater_than_half_max[-1]]
	left_time = bin_edges[locations_greater_than_half_max[0]]
	kappa = (right_time-left_time + bin_interval)/2  #in case the peak is one bin wide.
	offset = 0

	bin_centers = bin_edges[:-1]+bin_interval/2
	#format the parameters
	init_guess = [x0, amplitude, kappa, offset]

	#fit
	(best_guess, cov_best_guess) = leastsq(residuals_of_lorentzian, init_guess, args=(bin_centers,hist))
	y_model = [lorentzian(x, best_guess[0], best_guess[1], best_guess[2], best_guess[3],) for x in bin_centers]
	y = hist
	chi_sq = chi_2(y, y_model)


	return {"fcavity" : best_guess[0], "kappa" : best_guess[2], "dark_counts" : best_guess[3],"amplitude": best_guess[1], "covariance matrix":cov_best_guess, "chi_square": chi_sq}

def rabi_splitting_transmission(f, fatom, fcavity, Neta, gamma, kappa, dkcounts = 0):
	'''
	Returns the transmission through the cavity-atom system.


	f 		= probe frequency (EOM)
	fatom	= atomic frequency (in terms of probe frequency)
	fcavity = empty cavity frequency ("")
	Neta	= total cooperativity (single atom cooperativity eta times the total number of atoms in the up level)
	gamma  	= atomic transition linewidth (184kHz)
	kappa	= empty cavity linewidth (~500kHz)
	
	dkcounts= dark-counts per scan This should be implemented.

	'''
	# define some local variables to simplify the writing of the formula

	xa = 2*(f-fatom)/gamma
	xc = 2*(f-fcavity)/kappa

	return ((1+Neta/(1+xa**2))**2+(xc-Neta*xa/(1+xa**2))**2)**(-1)+dkcounts

def residuals_of_rabi_splitting_transmission(params, x_data, y_data):
	'''
	Returns the residuals of rabi_splitting fit
	'''
	#params[6] = amplitude;
	diff = [params[6]*rabi_splitting_transmission(x, params[0], params[1], params[2], params[3], params[4], params[5]) - (y) for x,y in zip(x_data,y_data)]
	return diff

def chi_2(y_data, y_model):
	'''
	Calculates the normalized chi^2 of a fitted model as: , where N is the total amount of data dtectd.

	'''

	try:
		total_chi_2 = [((y-ye)**2)/(y+1) for y,ye in zip(y_data,y_model)]
		return ((len(total_chi_2))**(-1/2))*sum(total_chi_2)
	except Exception as e:
		print("Failed calculating chi_square. Error:",e)

def fit_rabi_splitting_transmission(data,bnds={"fatom_range":(0,50), "fcavity_range":(0,50), "Neta_range":(0,20000)}, bin_interval=0.2, data_globals=None):

	''' Fits a rabi_splitting_data using least squares. Assumes unbinned photon
	arrival times for data.

	Returns best_guess and cov_best_guess
	## To dos

	[x] Try a parameter grid scan to find the region of global minima

	'''


	# get globals

	try:
		if DEBUG: print("Globals Imported Successfully during lstsq fit.")
	except:
		print("Failed Importing Globals during lstsq fit!")

	
		# define some fixed value. 
	# Try to get values from globals. If globals is missing, it will use some preset value.
	try:
		kappa_loc = data_globals['exp_cavity_kappa']*0.001 # 0.001 becasue in globals this is specified in kHz
	except:
		kappa_loc = 0.530
		print("Failed getting kappa from globals.")
	try:
		gamma_loc = data_globals['green_gamma']*0.001  # 0.001 becasue in globals this is specified in kHz
	except:
		gamma_loc = 0.184
	try:
		dark_counts = data_globals['dark_counts']*data_globals['empty_cavity_sweep_duration']*0.001
	except:
		dark_counts = 120*0.03

	# extract some parameter
	Neta_range   	= bnds["Neta_range"]
	fatom_range 	= bnds["fatom_range"]
	fcavity_range	= bnds["fcavity_range"]


	#bin the data
	(hist, bin_edges) = np.histogram(
		data,
		bins=np.arange(data[0]-1,data[-1]+1, bin_interval)
	)
	

	#estimate initial parameters

	fcavity_guess = np.mean(data)
	Neta_guess = 4.*np.var(data)/(gamma_loc * kappa_loc)
	# guess initial parameters, to fix the parameters, set the relative params_range to 0
	## check if guesses are in the set ranges, if not redefine the guesses
	try:
		if fcavity_guess < fcavity_range[0] or fcavity_guess > fcavity_range[1]:
			fcavity_guess = np.mean(fcavity_range)
	except:
		pass
	print("Initial Neta_guess ma azzo: ",Neta_guess)
	fatoms_guess =	fcavity_guess
	try:
		if fatoms_guess < fatom_range[0] or fatoms_guess > fatom_range[1]:
			fatoms_guess = np.mean(fatom_range)
	except Exception as e:
		print("fatoms_guess failed. Error:", e)
	try:
		if Neta_guess < Neta_range[0] or Neta_guess > Neta_range[1]:
			Neta_guess = np.mean(Neta_range)
	except:
		pass

	bin_centers=bin_edges[:-1]+bin_interval/2;
	if Neta_guess > 50:
		amplitude = sum(hist)/0.6*bin_interval
		grid_scan=1e9
		for Neta_grid in np.arange(Neta_guess*0.4, Neta_guess*1.4+1, Neta_guess/10):
			for fcav_grid in np.arange(fcavity_guess-0.5, fcavity_guess+2.1, .15):
				for fatoms_grid in np.arange(fatoms_guess-1, fatoms_guess+1, .25):
					try:
						init_guess_loc = (fatoms_grid,fcav_grid, Neta_grid, gamma_loc, kappa_loc, dark_counts, amplitude)
						residuals_tot_local=sum(square(residuals_of_rabi_splitting_transmission(init_guess_loc, bin_centers,hist)))/len(bin_centers)
						if grid_scan>residuals_tot_local:
							# print("Temporary Min of residuals:", residuals_tot_local)
							grid_scan = residuals_tot_local
							init_guess = init_guess_loc
					except Exception as e:
						init_guess = (fatoms_guess, fcavity_guess, Neta_guess, gamma_loc, kappa_loc, dark_counts, amplitude)
						print("----- Fucked up getting init_guess from grid. Error :",e)
		bnds_list = ((init_guess[0]-.5, init_guess[1]-.5, init_guess[2]*(1-1/10), gamma_loc-0.004, kappa_loc-0.05, 0,.25*amplitude),(init_guess[0]+.5, init_guess[1]+.5, init_guess[2]*(1+1/10), gamma_loc+0.001, kappa_loc+0.2, 10*dark_counts,4*amplitude))
	else:
		amplitude = sum(hist)/0.85*bin_interval
		init_guess = (fatoms_guess, fcavity_guess, Neta_guess, gamma_loc, kappa_loc, dark_counts, amplitude)
		bnds_list = ((fatom_range[0], fcavity_range[0], Neta_range[0], gamma_loc-0.004, kappa_loc-0.05, 0,.25*amplitude),(fatom_range[1], fcavity_range[1], Neta_range[1], gamma_loc+0.001, kappa_loc+0.2, 10*dark_counts,4*amplitude))

	#fit

	for s in range(len(init_guess)):
		if (init_guess[s]-bnds_list[0][s])<0:
			print("Initial value failed Element : ", s)
		if (init_guess[s]-bnds_list[1][s])>0:
			print("Initial value failed. Element : ", s)
	# print("fcavity_guess: ", init_guess[1])
	# print("fcavity_range: ", fcavity_range)

	out = least_squares(
		residuals_of_rabi_splitting_transmission, 
		init_guess, 
		args=(bin_centers,hist), 
		bounds =bnds_list
		)
	best_param=out.x
	#best_param=init_guess
	jac_best_guess=out.jac
	#jac_best_guess=1
	y_model = [best_param[6]*rabi_splitting_transmission(x, best_param[0], best_param[1], best_param[2], best_param[3], best_param[4], best_param[5]) for x in bin_centers]
	y = hist
	chi_sq = chi_2(y, y_model)


	return {"fatom": best_param[0], "fcavity" : best_param[1], "Neta": best_param[2], "gamma" : best_param[3], "kappa" : best_param[4], "dark_counts" : dark_counts,"amplitude": best_param[6], "jacobian":jac_best_guess, "chi_square": chi_sq}


def find_peaks(photon_frequencies, eps, clusterSize_ratio_cutoff = 15, DEBUG = False):
	'''
	Cluster data to find the two peaks. It then test if there are 2 peaks or most likely just one.

	photon_frequencies : frequencies of photons detected. They must be sorted
	eps :  is a parameter defining the distance between points in a cluster, ideally (kappa gamma)/2
	'''
	if DEBUG :
		print('eps = ',eps)
		print('diffMin', np.min(photon_frequencies[1:]-photon_frequencies[0:-1]))
	
	#some preparation
	clusters = [];
	curr_photon = photon_frequencies[0]
	curr_cluster = [curr_photon]
	for point in photon_frequencies[1:]:
		if point <= curr_photon + eps:
			curr_cluster.append(point)
		else:
			clusters.append(curr_cluster)
			curr_cluster = [point]
		curr_photon = point
	clusters.append(curr_cluster)
	clusters.sort(key = len)

	# we test here whether we have one peak or peaks 
	testPeaks = np.abs(np.mean(photon_frequencies) - np.mean(clusters[-1]))
	if len(clusters)>1: 
		ratio_of_clustersizes = len(clusters[-1])/len(clusters[-2])
	else:
		ratio_of_clustersizes = 2*clusterSize_ratio_cutoff

	if DEBUG: print("Clusters Siye Ratio :  ", ratio_of_clustersizes)

	if testPeaks < eps/4 or ratio_of_clustersizes > clusterSize_ratio_cutoff:
		if DEBUG: print('we have one peak!')
		return clusters[-1], 0
	else:
		if DEBUG: print('we have 2 peaks!')
		dist_peaks = np.abs(np.median(clusters[-2])-np.median(clusters[-1]))
		selected_photons = clusters[-2]+clusters[-1]
		selected_photons.sort()
		return np.array(selected_photons), dist_peaks

def calculate_histogram(photon_frequencies, frequency_range, bin_width):
	f = frequency_range
	bins = int((f[1] - f[0])/bin_width)

	return np.histogram(
			photon_frequencies,
			bins=bins,
			range=frequency_range,
			density=True
		)

def square_distribution(distribution, x_axis,power=2):
	'''
		Squares the probability distribution and then normalizes it.
	'''

	distribution = np.power(distribution,power)
	#integrate
	norm = np.trapz(distribution,x_axis)
	return distribution/norm

def return_moments(distribution,x_axis):
	integrand = np.multiply(distribution,x_axis)
	mean = np.trapz(integrand, x_axis)

	integrand = np.multiply(distribution,np.square(x_axis - mean))
	variance = np.trapz(integrand, x_axis)

	integrand = np.multiply(distribution,np.power(x_axis - mean,3))
	skweness = np.trapz(integrand, x_axis)
	return skweness, variance, mean

def logLikelihood_rabi_splitting_transmission(params, data):
	'''
	calculates the -loglikelihood of a set of data as a function of the other parameters. 
	Minus LL because we maximze the LL using minimize().

	data  			= list of frequencies of detected photons. They are obtained from photons arrival times.
	params		= (fatom, fcavity, Neta, gamma, kappa, dkcounts)
	
	'''
	rabi_splitting_transmission_Integral = 0.61 # for Neta>>1 the Rabi splitting integral formula converges to this value

	i = data

	LL_perpoint = - np.log(rabi_splitting_transmission(i,params[0],params[1],params[2],params[3],params[4],dkcounts=params[5]))
	
	return sum(LL_perpoint)/len(data)

def logLikelihood_empty_cavity_transmission(params, data,):
	'''
	calculates the -loglikelihood of a set of data as a function of the other parameters. 
	Minus LL because we maximze the LL using minimize().

	data  			= list of frequencies of detected photons. They are obtained from photons arrival times.
	params		= (fcavity, kappa, dkcounts (offset))

	## To Dos

	[] consider correctly darkcounts
	
	'''
	i = data
	LL_perpoint = -np.log(lorentzian(i, params[0],1, params[1], 0))
	#LL_perpoint = np.log(lorentzian(data, params[0], 1, params[1], params[2]))
	
	return sum(LL_perpoint)/len(data)


def fit_single_cavity_peak_MLE(data, data_globals,bin_interval=0.2):
	''' Fits a single_cavity_peak using MLE. Assumes unbinned photon
	arrival times for data.

	## To Do

	[] Implement method to extract covariance matrix / parameters error
	'''

	try:
		if DEBUG: print("Globals imported successfully during MLE Fit") 
	except:
		print("Failed Importing Globals during MLE fit ")

	# define some fixed value. 
	# Try to get values from globals. If globals is missing, it will use some preset value.
	try:
		kappa_loc = data_globals['exp_cavity_kappa']*0.001 # 0.001 becasue in globals this is specified in kHz
	except Exception as e:
		kappa_loc = 0.530
		print("Failed getting kappa from globals. kappa_loc =", kappa_loc,"\n Error : ",e)

	#remove data from wings very far away. This photons are either dark counts or carry very low Fisher information.
	data =  data[round(len(data)*0.05) : round(len(data)*0.95)]

	#estimate initial parameters
	fcavity = np.median(data)
	offset = 0

	#format the parameters
	init_guess = [fcavity, kappa_loc/2, offset]

	#fit
	out = minimize(logLikelihood_empty_cavity_transmission, init_guess, args=data)
	
	best_guess = out.x

	(hist, bin_edges) = np.histogram(
				data,
				bins=np.arange(data[0]-1,data[-1]+1, bin_interval)
			)
	bin_centers=bin_edges[:-1]+bin_interval/2

	amp_guess = sum(hist)*bin_interval
	y_model = [lorentzian(x, best_guess[0], amp_guess, best_guess[1], best_guess[2],) for x in bin_centers]
	y = hist
	chi_sq = chi_2(y, y_model)


	return {"fcavity" : init_guess[0], "kappa" : init_guess[1], "dark_counts" : init_guess[2],"amplitude": amp_guess, "chi_square": chi_sq, "number_of_detected_photons" : len(data)}

def fit_rabi_splitting_transmission_MLE(data, bnds={"fatom_range":(0,50), "fcavity_range":(0,50), "Neta_range":(0,20000)}, param_error = 'off', bs_repetition = 25, data_globals=None, bin_interval=0.2, DEBUG = False):
	'''
	Fits the Rabi Splitting in a scan experiment with Maximum Likelihood Estimator (MLE). Returns the Neta.
	
	output = fit_rabi_splitting_transmission_MLE(data,bnds,param_error,bs_repetition)


	data			: list of frequencies of detected photons. They are obtained from photons arrival times.
	bnds			: dictionary specifying parameters's ranges (fatoms, fcavity, Neta)

	param_error  		: if turned on, the function estimates parameters error by bootstrapping the data
	bs_repetition	: specify how many bootstrapped datasample are we analyzing to perform statistics on fit

	output			: tuple with a MLE result as first element; it is a 3 elements ndarray reporting (fatoms, fcavity, Neta). 
	      				  When param_error='on' the output tuple contains the covariance matrix of the fitted parameters as second element. The second element is absent if param_error='off'.


	frequency unit: MHz

	We first scan a coars grid of params to get nice initial condition for maximizing the LogLikelihood function.
	
	## Why we used bootstrapping method 
	
	The presence of bounds in fit parameters significantly increments the complexity in estimating uncertainties and correlations. This is due to the fact that it bacomes hard (if not impossible) to correctly calculate the Hessian matrix in the presence of bounds.
	Therefore, to estimate the covariance matrix of the fitted parameters, we bootstrap the data (bootsrapping method). This allows us to estimate fit parameters and the experimental covariance matrix without computing Hessians or Jacobian.

	
	
	### What is bootstrapping?
	
	Bootstrapping is a method widely used in statistics. Bootstrapping is any test or metric that uses random sampling with replacement (e.g. mimicking the sampling process). This technique allows estimation of the sampling distribution of almost any statistic using random sampling methods.

	The idea is to create a set of n "measurements" sampled from data with the same statistical properties as the data itself. We then perform the MLE fit to each of these n resampled data. Finally, we can extract mean values for the fit parameters and the experimental covariance matrix.

	For deatails, see : https://en.wikipedia.org/wiki/Bootstrapping_%28statistics%29
	
	`bin_interval` : It is used to calculate chi_square. To do so, we bin the data and get the resulting histogram, we let our model have the same integral as the histogram_data (sum of all bars area -> amp*bin:interval), and calcuate chi_square yield by the difference between histograms and model. It is also used to get an amplitude estimation for plotting data and fit.

	## To dos

	[] set the eps parameter as being dependent on the photon number. (With np->inf, we have a single cluster)
	[] Fix f_cavity when needed
	'''
	try:
		if DEBUG: print("Globals imported successfully during MLE Fit") 
	except:
		print("Failed Importing Globals during MLE fit ")

	# define some fixed value. 
	# Try to get values from globals. If globals is missing, it will use some preset value.
	try:
		kappa_loc = data_globals['exp_cavity_kappa']*0.001 # 0.001 becasue in globals this is specified in kHz
	except:
		kappa_loc = 0.530
		print("Failed getting kappa from globals.")

	try:
		gamma_loc = data_globals['green_gamma']*0.001  # 0.001 becasue in globals this is specified in kHz
	except:
		gamma_loc = 0.184

	try:
		fix_fatom = data_globals['fix_f_atoms']
	except:
		fix_fatom = True
		print("Failed getting fix_f_atoms from globals.")


	try: #not yet correct
		dark_counts = data_globals['dark_counts']*data_globals['empty_cavity_sweep_duration']*0.01
	except:
		dark_counts = 120*0.1


	# if DEBUG: print("set Dark counts :", dark_counts)
	
	# extract some parameter
	Neta_range   	= bnds["Neta_range"]
	fatom_range  	= bnds["fatom_range"]
	fcavity_range	= bnds["fcavity_range"]
	

	#We use a clustering algorithm (Agglomeration Clustering) to find the two peaks, do some extra test to check if the peaks are 2 or just 1.

	eps = (kappa_loc*gamma_loc)**(0.5)/2
	data, dist_peaks = find_peaks(photon_frequencies=data, eps=eps)

	#remove data from wings very far away. This photons are either dark counts or carry very low Fisher information.
	#if len(data)>20 : data =  data[round(len(data)*0.00) : round(len(data)*0.96)]

	# guess initial parameters, to fix the parameters, set the relative params_range to 0
	#estimate initial parameters

	distribution, frequency_axis = calculate_histogram(
		photon_frequencies=data,
		frequency_range=(data[0], data[-1]),
		bin_width=bin_interval
		)

	Neta_guess = dist_peaks**2/(kappa_loc*gamma_loc)

	POWER = 2
	distribution = square_distribution(distribution,frequency_axis[:-1],POWER)
	skew, var, mean = return_moments(distribution,frequency_axis[:-1])

	diff_cavity_atoms = -(skew/var)/2.5;
	fcavity_guess = mean
	if fix_fatom : 
		# check if we have a fixed f_atoms 
		try:
			fatoms_guess = data_globals['f_atoms']
		except:
			fatoms_guess = 15.6
	else:
		fatoms_guess = fcavity_guess-diff_cavity_atoms

	# guess initial parameters, to fix the parameters, set the relative params_range to 0
	## check if guesses are in the set ranges, if not redefine the guesses

	try:
		if fcavity_guess < fcavity_range[0] or fcavity_guess > fcavity_range[1]:
			fcavity_guess = np.mean(fcavity_range)
	except:
		pass
	print("Initial Neta_guess FUG: ",Neta_guess)
	
	try:
		if fatoms_guess < fatom_range[0] or fatoms_guess > fatom_range[1]:
			fatoms_guess = np.mean(fatom_range)
	except Exception as e:
		print("fatoms_guess failed. Error:", e)
	try:
		if Neta_guess < Neta_range[0] or Neta_guess > Neta_range[1]:
			Neta_guess = np.mean(Neta_range)
	except:
		pass
	
	# Set coarse parameter's grid. Need to find a location near around the global minimum (or floal MaxLL)
	if Neta_guess > 0 :	Neta_gridpoints = np.arange(Neta_guess*0.99, Neta_guess*1.01, Neta_guess/10)
	if fix_fatom:
		if DEBUG : print('FREQ ATOMS FIXED')
		fatom_gridpoints = np.array([fatoms_guess])
	else:
		if DEBUG : print('FREQ ATOMS NOT FIXED !!!')
		fatom_gridpoints = np.arange(fatoms_guess-2., fatoms_guess+2., .25)
	fcav_gridpoints = np.arange(fcavity_guess-1, fcavity_guess+1.5, .25)

	if Neta_guess > 10:
		grid_scan=0
		for Neta_grid in Neta_gridpoints:
			for fcav_grid in fcav_gridpoints:
				for fatoms_grid in fatom_gridpoints:
					try:
						init_guess_loc = (fatoms_grid,fcav_grid, Neta_grid, gamma_loc, kappa_loc, dark_counts)
						LL_tot_loc=logLikelihood_rabi_splitting_transmission(init_guess_loc, data)
						if grid_scan>LL_tot_loc:
							if DEBUG: print("Temporary Min of -LL:", LL_tot_loc)
							grid_scan = LL_tot_loc
							init_guess = init_guess_loc
					except Exception as e:
						init_guess = (fatoms_guess, fcavity_guess, Neta_guess, gamma_loc, kappa_loc, dark_counts)
						print("----- Fucked up getting init_guess from grid. Error :",e)
		bnds_list = ((init_guess[0]-.7, init_guess[0]+.7), (init_guess[1]-.25,init_guess[1]+.25), (init_guess[2]*(1-1/5),init_guess[2]*(1+1/5)), (gamma_loc-0.001,gamma_loc+0.001),( kappa_loc-0.001, kappa_loc+0.001), (0, 0.00001*dark_counts))
	else:
		grid_scan=0
		fatom_guess = fcavity_guess
		for Neta_grid in np.arange(0, 20, 5):
			for fcav_grid in np.arange(fcavity_guess-.2, fcavity_guess+.2, .1):
				for fatoms_grid in np.arange(fatoms_guess-0.2, fatoms_guess+.2, .1):
					try:
						init_guess_loc = (fatoms_grid,fcav_grid, Neta_grid, gamma_loc, kappa_loc, dark_counts)
						LL_tot_loc=logLikelihood_rabi_splitting_transmission(init_guess_loc, data)
						if grid_scan>LL_tot_loc:
							if DEBUG: print("Temporary Min of -LL:", LL_tot_loc)
							grid_scan = LL_tot_loc
							init_guess = init_guess_loc
					except Exception as e:
						init_guess = (fatoms_guess, fcavity_guess, Neta_guess, gamma_loc, kappa_loc, dark_counts)
						print("----- Fucked up getting init_guess from grid. Error :",e)
		bnds_list = ((init_guess[0]-.2, init_guess[0]+.2), (init_guess[1]-.25,init_guess[1]+.25), (init_guess[2]*(1-1/5),init_guess[2]*(1+1/5)), (gamma_loc-0.001,gamma_loc+0.001),( kappa_loc-0.001, kappa_loc+0.001), (0, 0.00001*dark_counts))

		# init_guess = (fatoms_guess, fcavity_guess, Neta_guess, gamma_loc, kappa_loc, dark_counts)
		# bnds_list = (fatom_range, fcavity_range, Neta_range, (gamma_loc-0.001,gamma_loc+0.001),( kappa_loc-0.001, kappa_loc+0.001), (0, 0.0001*dark_counts))
	#fit

	if param_error == 'on':
		# bootstrap the data and perform MLE fit for all databs. Then do statistics of bootstrapped results
		# This method may be slow. It can be improved in speed by implementing Hessian matrix calculations, however it may be tricky because of bounds.
		bs_list=[]
		for i in np.arange(bs_repetition):
			data_bs = random.choices(data,k=len(data))
			out=minimize(logLikelihood_rabi_splitting_transmission, init_guess,args=data_bs, bounds=bnds_list, tol=0.001)
			bs_list.append(out.x)
		best_param= np.mean(np.transpose(bs_list),1)
		cov = np.sqrt(np.transpose(bs_list)) # Covariance matrix
		
		#bin the data
		#bin_interval=0.2
		(hist, bin_edges) = np.histogram(
			data,
			bins=np.arange(data[0]-1,data[-1]+1, bin_interval)
			)
		bin_centers=bin_edges[:-1]+bin_interval/2

		amp_guess = [sum(hist)/0.6*bin_interval]

		y_model = [amp_guess[0]*rabi_splitting_transmission(x, best_param[0], best_param[1], best_param[2], best_param[3], best_param[4], 0) for x in bin_centers]
		y = hist

		chi_sq = chi_2(y, y_model)

		best_param = {"fatom" : best_param[0], "fcavity" : best_param[1], "Neta": best_param[2],  "gamma" : best_param[3], "kappa" : best_param[4], "dark_counts" : best_param[5], 'amplitude':amp_guess,'covariance' : cov,"chi_square" : chi_sq, "number_of_detected_photons" : len(data), "Neta_guess" : Neta_guess} # gamma and kappa are not fit parameters!
		return best_param

	elif param_error == 'off':
		out = minimize(logLikelihood_rabi_splitting_transmission, init_guess,args=data,bounds=bnds_list)
		best_param = out.x

		# Get the chi_2
		#bin the data
		(hist, bin_edges) = np.histogram(
			data,
			bins=np.arange(data[0]-1,data[-1]+1, bin_interval)
			)
		bin_centers=bin_edges[:-1]+bin_interval/2

		amp_guess = sum(hist)/0.6*bin_interval
				
		y_model = [amp_guess*rabi_splitting_transmission(x, best_param[0], best_param[1], best_param[2], best_param[3], best_param[4], 0) for x in bin_centers]
		y = hist

		chi_sq = chi_2(y, y_model)

		return {"fatom": best_param[0], "fcavity" : best_param[1], "Neta": best_param[2], "gamma" : best_param[3], "kappa" : best_param[4], "dark_counts" : best_param[5],"amplitude" : amp_guess, "chi_square" : chi_sq, "number_of_detected_photons" : len(data), "Neta_guess" : Neta_guess }
	else :
		return('incorrect param_error specification')


def fit_rabi_splitting_transmission_MLE_OLD(data, bnds={"fatom_range":(0,50), "fcavity_range":(0,50), "Neta_range":(0,20000)}, param_error = 'off', bs_repetition = 25, data_globals=None, bin_interval=0.2):
	'''
	Fits the Rabi Splitting in a scan experiment with Maximum Likelihood Estimator (MLE). Returns the Neta.
	
	output = fit_rabi_splitting_transmission_MLE(data,bnds,param_error,bs_repetition)


	data			: list of frequencies of detected photons. They are obtained from photons arrival times.
	bnds			: dictionary specifying parameters's ranges (fatoms, fcavity, Neta)

	param_error  		: if turned on, the function estimates parameters error by bootstrapping the data
	bs_repetition	: specify how many bootstrapped datasample are we analyzing to perform statistics on fit

	output			: tuple with a MLE result as first element; it is a 3 elements ndarray reporting (fatoms, fcavity, Neta). 
	      				  When param_error='on' the output tuple contains the covariance matrix of the fitted parameters as second element. The second element is absent if param_error='off'.


	frequency unit: MHz

	We first scan a coars grid of params to get nice initial condition for maximizing the LogLikelihood function.
	
	## Why we used bootstrapping method 
	
	The presence of bounds in fit parameters significantly increments the complexity in estimating uncertainties and correlations. This is due to the fact that it bacomes hard (if not impossible) to correctly calculate the Hessian matrix in the presence of bounds.
	Therefore, to estimate the covariance matrix of the fitted parameters, we bootstrap the data (bootsrapping method). This allows us to estimate fit parameters and the experimental covariance matrix without computing Hessians or Jacobian.

	
	
	### What is bootstrapping?
	
	Bootstrapping is a method widely used in statistics. Bootstrapping is any test or metric that uses random sampling with replacement (e.g. mimicking the sampling process). This technique allows estimation of the sampling distribution of almost any statistic using random sampling methods.

	The idea is to create a set of n "measurements" sampled from data with the same statistical properties as the data itself. We then perform the MLE fit to each of these n resampled data. Finally, we can extract mean values for the fit parameters and the experimental covariance matrix.

	For deatails, see : https://en.wikipedia.org/wiki/Bootstrapping_%28statistics%29
	
	`bin_interval` : It is used to calculate chi_square. To do so, we bin the data and get the resulting histogram, we let our model have the same integral as the histogram_data (sum of all bars area -> amp*bin:interval), and calcuate chi_square yield by the difference between histograms and model. It is also used to get an amplitude estimation for plotting data and fit.

	## To dos

	[] include/consider correctly dark counts in MLE analysis
	[x] correct and update analysis for bootstrapping
	[] improve result saving for bootstrapped analysis. So far we just save the covariance matrix (enough info to use it, but one may need to dig back in the code to find out the entry orders)
	[] test performances for small Neta (and adapt amplitude for Neta~0)
	'''
	try:
		if DEBUG: print("Globals imported successfully during MLE Fit") 
	except:
		print("Failed Importing Globals during MLE fit ")

	# define some fixed value. 
	# Try to get values from globals. If globals is missing, it will use some preset value.
	try:
		kappa_loc = data_globals['exp_cavity_kappa']*0.001 # 0.001 becasue in globals this is specified in kHz
	except:
		kappa_loc = 0.530
		print("Failed getting kappa from globals.")
	try:
		gamma_loc = data_globals['green_gamma']*0.001  # 0.001 becasue in globals this is specified in kHz
	except:
		gamma_loc = 0.184
	try: #not yet correct
		dark_counts = data_globals['dark_counts']*data_globals['empty_cavity_sweep_duration']*0.001
	except:
		dark_counts = 120*0.03 
	if DEBUG: print("set Dark counts :", dark_counts)
	
	# extract some parameter
	Neta_range   	= bnds["Neta_range"]
	fatom_range  	= bnds["fatom_range"]
	fcavity_range	= bnds["fcavity_range"]
	
	#remove data from wings very far away. This photons are either dark counts or carry very low Fisher information.
	if len(data)>20 : data =  data[round(len(data)*0.04) : round(len(data)*0.96)]

	# guess initial parameters, to fix the parameters, set the relative params_range to 0
	#estimate initial parameters

	distribution, frequency_axis = calculate_histogram(
		photon_frequencies=data,
		frequency_range=(data[0], data[-1]),
		bin_width=bin_interval
		)

	POWER = 2
	distribution = square_distribution(distribution,frequency_axis[:-1],POWER)
	skew, var, mean = return_moments(distribution,frequency_axis[:-1])

	diff_cavity_atoms = -(skew/var)/2.5;
	fcavity_guess = mean
	fatoms_guess = fcavity_guess-diff_cavity_atoms
	Neta_guess = 4.*(var-kappa_loc/4)/(gamma_loc * kappa_loc)
	# guess initial parameters, to fix the parameters, set the relative params_range to 0
	## check if guesses are in the set ranges, if not redefine the guesses

	try:
		if fcavity_guess < fcavity_range[0] or fcavity_guess > fcavity_range[1]:
			fcavity_guess = np.mean(fcavity_range)
	except:
		pass
	print("Initial Neta_guess FUG: ",Neta_guess)
	
	try:
		if fatoms_guess < fatom_range[0] or fatoms_guess > fatom_range[1]:
			fatoms_guess = np.mean(fatom_range)
	except Exception as e:
		print("fatoms_guess failed. Error:", e)
	try:
		if Neta_guess < Neta_range[0] or Neta_guess > Neta_range[1]:
			Neta_guess = np.mean(Neta_range)
	except:
		pass
	# Do some magic and fit two Lorentzian


	if Neta_guess > 40:
		grid_scan=0
		for Neta_grid in np.arange(Neta_guess*0.7, Neta_guess*1.2, Neta_guess/10):
			for fcav_grid in np.arange(fcavity_guess-2, fcavity_guess+2, .25):
				for fatoms_grid in np.arange(fatoms_guess-2., fatoms_guess+2., .25):
					try:
						init_guess_loc = (fatoms_grid,fcav_grid, Neta_grid, gamma_loc, kappa_loc, dark_counts)
						LL_tot_loc=logLikelihood_rabi_splitting_transmission(init_guess_loc, data)
						if grid_scan>LL_tot_loc:
							if DEBUG: print("Temporary Min of -LL:", LL_tot_loc)
							grid_scan = LL_tot_loc
							init_guess = init_guess_loc
					except Exception as e:
						init_guess = (fatoms_guess, fcavity_guess, Neta_guess, gamma_loc, kappa_loc, dark_counts)
						print("----- Fucked up getting init_guess from grid. Error :",e)
		bnds_list = ((init_guess[0]-.75, init_guess[0]+.75), (init_guess[1]-.75,init_guess[1]+.75), (init_guess[2]*(1-1/5),init_guess[2]*(1+1/5)), (gamma_loc-0.001,gamma_loc+0.001),( kappa_loc-0.0001, kappa_loc+0.0001), (0, 0.1*dark_counts))
	else:
		grid_scan=0
		#fatom_guess = fcavity_guess
		for Neta_grid in np.arange(Neta_guess*0.5, Neta_guess*1.21, Neta_guess/10):
			for fcav_grid in np.arange(fcavity_guess-2, fcavity_guess+2, .2):
				for fatoms_grid in np.arange(fatoms_guess-2., fatoms_guess+2., .2):
					try:
						init_guess_loc = (fatoms_grid,fcav_grid, Neta_grid, gamma_loc, kappa_loc, dark_counts)
						LL_tot_loc=logLikelihood_rabi_splitting_transmission(init_guess_loc, data)
						if grid_scan>LL_tot_loc:
							if DEBUG: print("Temporary Min of -LL:", LL_tot_loc)
							grid_scan = LL_tot_loc
							init_guess = init_guess_loc
					except Exception as e:
						init_guess = (fatoms_guess, fcavity_guess, Neta_guess, gamma_loc, kappa_loc, dark_counts)
						print("----- Fucked up getting init_guess from grid. Error :",e)
		bnds_list = ((init_guess[0]-.75, init_guess[0]+.75), (init_guess[1]-.75,init_guess[1]+.75), (init_guess[2]*(1-1/5),init_guess[2]*(1+1/5)), (gamma_loc-0.001,gamma_loc+0.001),( kappa_loc-0.0001, kappa_loc+0.0001), (0, 0.1*dark_counts))

		#init_guess = (fatoms_guess, fcavity_guess, Neta_guess, gamma_loc, kappa_loc, dark_counts)
		#bnds_list = (fatom_range, fcavity_range, Neta_range, (gamma_loc-0.004,gamma_loc+0.004),( kappa_loc-0.1, kappa_loc+0.15), (0, 0.0001*dark_counts))
	#fit

	if param_error == 'on':
		# bootstrap the data and perform MLE fit for all databs. Then do statistics of bootstrapped results
		# This method may be slow. It can be improved in speed by implementing Hessian matrix calculations, however it may be tricky because of bounds.
		bs_list=[]
		for i in np.arange(bs_repetition):
			data_bs = random.choices(data,k=len(data))
			out=minimize(logLikelihood_rabi_splitting_transmission, init_guess,args=data_bs, bounds=bnds_list, tol=0.001)
			bs_list.append(out.x)
		best_param= np.mean(np.transpose(bs_list),1)
		cov = np.sqrt(np.transpose(bs_list)) # Covariance matrix
		
		#bin the data
		#bin_interval=0.2
		(hist, bin_edges) = np.histogram(
			data,
			bins=np.arange(data[0]-1,data[-1]+1, bin_interval)
			)
		bin_centers=bin_edges[:-1]+bin_interval/2

		amp_guess = [sum(hist)/0.6*bin_interval]

		y_model = [amp_guess[0]*rabi_splitting_transmission(x, best_param[0], best_param[1], best_param[2], best_param[3], best_param[4], 0) for x in bin_centers]
		y = hist

		chi_sq = chi_2(y, y_model)

		best_param = {"fatom" : best_param[0], "fcavity" : best_param[1], "Neta": best_param[2],  "gamma" : best_param[3], "kappa" : best_param[4], "dark_counts" : best_param[5], 'amplitude':amp_guess,'covariance' : cov,"chi_square" : chi_sq, "number_of_detected_photons" : len(data)} # gamma and kappa are not fit parameters!
		return best_param

	elif param_error == 'off':
		out = minimize(logLikelihood_rabi_splitting_transmission, init_guess,args=data,bounds=bnds_list)
		best_param = out.x

		# Get the chi_2
		#bin the data
		(hist, bin_edges) = np.histogram(
			data,
			bins=np.arange(data[0]-1,data[-1]+1, bin_interval)
			)
		bin_centers=bin_edges[:-1]+bin_interval/2

		amp_guess = sum(hist)/0.6*bin_interval
				
		y_model = [amp_guess*rabi_splitting_transmission(x, best_param[0], best_param[1], best_param[2], best_param[3], best_param[4], 0) for x in bin_centers]
		y = hist

		chi_sq = chi_2(y, y_model)

		return {"fatom": best_param[0], "fcavity" : best_param[1], "Neta": best_param[2], "gamma" : best_param[3], "kappa" : best_param[4], "dark_counts" : best_param[5],"amplitude" : amp_guess, "chi_square" : chi_sq, "number_of_detected_photons" : len(data)}
	else :
		return('incorrect param_error specification')



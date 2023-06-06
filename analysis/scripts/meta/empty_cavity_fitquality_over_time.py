''' This metanalysis will plot and analyse the fit quality ofer the time. It
will be used to monitor how fitting Rabi splitting works over the time and/or
as a function of experimental parameters

 # To Do 
 	[x] make empty_cavity_helper.py write the chi^2 value (and/or LogLikelihood) of fit in lyse parameters
 	[x] read lyse parameters here
 	[x] plot chi^2 over the time
 	[] statistics (hist plot, for example) of chi^2 results
 	[] statistics versus some interesting parameter, like photons detected for example

'''

from lyse import *
import pickle
import numpy as np
import matplotlib.pyplot as plt

if __name__ == '__main__':
	try:
		#exposes all the variables available in the lyse window
		dataframe = data()


		runtimes = list(dataframe['run time'])
		paths = list(dataframe['filepath'])
		fit_quality = list(dataframe['empty_cavity_helper','chi_square_1'])
		#this is what we call the run number. we'll use it to change the color, so we can tell when we changed the sequence.
		sequence_index = list(dataframe['sequence_index'])


		#make some colors.
		cerulean = (4/256,146/256,194/256)
		crimson = (185/256, 14/256, 10/256)
		colors = [cerulean if seq%2 == 0 else crimson for seq in sequence_index]

		#Calculate and print Good Fit Ratio
		good_chi_for_fit = [0.5,10]

		is_good_fit = []
		for set_of_fits in fit_quality:
			for fit in set_of_fits:
				is_good_fit.append(
						(fit > good_chi_for_fit[0]) and (fit < good_chi_for_fit[1])
					)

		good_fit_ratio = sum(is_good_fit)/len(is_good_fit)

		#s - size
		plt.scatter(sequence_index, fit_quality, s=20, c = colors)

		plt.title("Empty Fit Quality\n" + f"Good Fit Ratio: {100*good_fit_ratio:.1f}%")
		plt.ylabel("chi squared")
		plt.xlabel("sequence index")
	except Exception as e:
		print(f"Empty Cavity Fit: {e}")
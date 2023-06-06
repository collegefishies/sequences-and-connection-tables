''' This metanalysis will plot and analyse the initially loaded Neta versus the time. It
will be used: 
i) to monitor how fitting Rabi splitting works over the time and/or
as a function of experimental parameters
ii) to test the loading efficiency, the output can be used to optimize loading

 # To Do 
 	[x] make atoms_in_cavity_helper.py write the Neta 1 value per scan number of fit in lyse parameters
 	[x] read lyse parameters here
 	[x] drop Neta based on bad chi^2 
 	[] multiple scan number and different color for different scan number in the sequence
 	[] statistics (hist plot, for example) of Neta results

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
		fit_1_quality = list(dataframe['atoms_in_cavity_helper','chi_square_1'])
		Neta_1_list = list(dataframe['atoms_in_cavity_helper','Neta_2'])
		#this is what we call the run number. we'll use it to change the color, so we can tell when we changed the sequence.
		sequence_index = list(dataframe['sequence_index'])

		#make some colors.
		cerulean = (4/256,146/256,194/256)
		crimson = (185/256, 14/256, 10/256)
		colors = [cerulean if seq%2 == 0 else crimson for seq in sequence_index]
		blue = [(0,0,1)]
		red = [(1,0,0)]

		#Calculate and print Good Fit Ratio
		good_chi_for_fit = [0.4,25]

		is_good_fit = []
		for fit in fit_1_quality:
			is_good_fit.append(
					(fit > good_chi_for_fit[0]) and (fit < good_chi_for_fit[1])
				)
		
		# create a list of lists with data we may want to plot, with `is_good_fit`. as the first element of each line.
		data_for_fit = np.transpose([fit_1_quality, sequence_index, runtimes, Neta_1_list]) # 
		# select good runs
		data_sel_for_fit = []
		for data_set in data_for_fit:
				fit = data_set[0]
				if (fit > good_chi_for_fit[0]) and (fit < good_chi_for_fit[1]):
					data_sel_for_fit.append(data_set)
		data_sel_for_fit = np.transpose(data_sel_for_fit)

		print(True+True)
		#s - size
		plt.scatter(runtimes, Neta_1_list, s=20, c = red)

		plt.scatter(data_sel_for_fit[-2], data_sel_for_fit[-1], s=40, c = blue)

		plt.title("Fitted Neta" )
		plt.ylabel("Neta")
		plt.xlabel("Time")


	except Exception as e:
		print(f"Rabi Splitting: {e}")
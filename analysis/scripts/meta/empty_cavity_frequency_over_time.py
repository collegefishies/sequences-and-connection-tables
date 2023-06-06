'''
	Plot's the Empty Cavity Frequency over Time.

	Currently it changes plot point color depending on the parity of the sequence
	number. This helps keep track of changes to the sequence. This feature is
	kind of useless seeing as with feedback the sequence will change every shot.

'''
from lyse import *
import pickle
import numpy as np
import matplotlib.pyplot as plt

def avg(l):
	return np.nanmean(l)

size = 20
if __name__ == '__main__':
	try:
		#exposes all the variables available in the lyse window
		dataframe = data(n_sequences=100)
		dataframe = data()


		runtimes = list(dataframe['run time'])
		paths = list(dataframe['filepath'])
		frequencies = np.array(dataframe['empty_cavity_helper','fcavity_1'])
		drive_frequencies = np.array(dataframe['bridging_frequency_759'])
		drive_frequencies = drive_frequencies - avg(drive_frequencies) + avg(frequencies) + 1
		#this is what we call the run number. we'll use it to change the color, so we can tell when we changed the sequence.
		sequence_index = list(dataframe['sequence_index'])


		#make some colors.
		cerulean = (4/256,146/256,194/256)
		crimson = (185/256, 14/256, 10/256)
		colors = [cerulean if seq%2 == 0 else crimson for seq in sequence_index]


		#s - size
		plt.scatter(runtimes, frequencies, s=size, color = crimson, label='exp_cavity_frequency')
		plt.scatter(runtimes, drive_frequencies,s=size, color= cerulean, label='bridging_frequency_759')
		# plt.scatter(runtimes, frequencies, s=20, c = colors)

		plt.legend()
		plt.title("Empty Cavity Frequency")
		plt.ylabel("Frequency (MHz)")
		plt.xlabel("Time")

	except Exception as e:
		print(e)

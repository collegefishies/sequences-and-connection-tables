'''

	Plots all photon arrival times out. Merely a Diagnostic Tool. Bins the data
	into 200 parts according to experimental run time.

'''

from lyse import *
import numpy as np
import matplotlib.pyplot as plt
from labscriptlib.ybclock.analysis.functions.metadata import extract_sequence_repetition_numbers, extract_date,extract_sequence_name
import labscriptlib.ybclock.analysis.functions.fit_functions as fit_functions
import matplotlib as mpl
mpl.rcParams['toolbar'] = 'None' 

if __name__ == '__main__':

	run = Run(path)

	#extract metadata
	(sequence_number, repetition_number)	= extract_sequence_repetition_numbers(path)
	date                                	= extract_date(path)
	sequence_name                       	= extract_sequence_name(path)

	try:
		#extract data
		photon_arrival_times = run.get_result_array(group='extract_photon_arrival_times',name='processed_arrivals_ch_1')

		#plot data
		plt.hist(
			photon_arrival_times,
			bins=np.arange(photon_arrival_times[0], photon_arrival_times[-1], photon_arrival_times[-1]/2000),
			align='mid'
		)

		#decorate plot
		plt.title(f"({date}) #{sequence_number}_r{repetition_number}\n{sequence_name}")
		plt.ylabel(f"Photon Counts, ({photon_arrival_times[-1]/200  *1000:.3g}ms Bin)")
		plt.xlabel("Time (s)")
	except:
		print("No Photon Data to Plot.")
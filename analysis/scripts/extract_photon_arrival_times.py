'''

	extracts photon arrival times from the single shot .lst file and converts
	them to absolute time, i.e., from the start of the experiment.

	`arrival_times` is a list of lists of arrival times for each photon in each channel.

	This is done manually. So if you want tips on how to extract data manually
	from the HDF file look here.

	Saves the results as attributes to the '/data/photon_arrivals' group
'''
from lyse import path, Run

#Add in libraries for working with HDF files
import labscript_utils.h5_lock
import h5py

#analysis libs
import numpy as np
import labscriptlib.ybclock.analysis.functions.photon_counter as photon_counter

VERBOSE = False

import os, sys

class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout


if __name__ == '__main__':
	with HiddenPrints():
		#load data from the last run
		path #path is defined in `from lyse ...`

		try:
			#extract the .lst binarys
			with h5py.File(path,'a') as hdf:
				arrival_lst_binary = np.array(hdf['/data/photon_arrivals/all_arrivals'])
				arrival_lst_bytestr = arrival_lst_binary.tobytes()

			#process the .lst binary
			(_,newline)                	= photon_counter.determine_newline_type(arrival_lst_bytestr)
			(header, data)             	= photon_counter.split_file_into_header_and_data(entire_file=arrival_lst_bytestr, newline=newline)
			header                     	= photon_counter.decode_header(header,verbose=False)
			(channels, quantized_times)	= photon_counter.decode_data(data, verbose=False)
			arrival_times              	= photon_counter.convert_to_absolute_time(t0=0, channels=channels,quantized_times=quantized_times, start_trigger_period=1e-3, quantized_time_unit=2e-9,path=path)
			
			#save the processed variables to the hdf files
			run = Run(path)
			processed_arrivals = {}

			for i in range(4):
				run.save_result_array(
					name	= f'processed_arrivals_ch_{i}',
					data	= np.array(arrival_times[i])
					)

			print("Saved processed_arrivals in hdf.")
		except:
			print("Could not extract photon_arrivals.")

		

		
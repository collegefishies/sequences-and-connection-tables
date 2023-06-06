'''This is the script for simply transferring data from the labscript system to
the old matlab system.

This involves just writing an .lst file to the 'exp_data_folder'
'''
from lyse import *
#Add in libraries for working with HDF files
import labscript_utils.h5_lock
import h5py
import numpy as np

import os
import datetime
from os import mkdir
from os.path import isfile, isdir, join

#get the date
now = datetime.datetime.now()

#don't run if it's somewhere from 12 am - 6 am.
#now.hour is in 24h time.
if now.hour < 6:
	print("I'm assuming you're not trying to start a new experiment past\
	midnight. Go to sleep! No data for you!")
	# quit()

#otherwise...
#
#

#declare our variables
exp_data_folder = 'E:\\Documents\\Experimental data'
this_months_folder = f"{now.year}_{now.month:02}"
todays_folder_prefix = f"{now.year}_{now.month:02}_{now.day:02}"


def return_months_last_data_folder(year, month, makedirectory=False):
	''' Return the folder name that has data for the given year and month. Create
	said folder if makedirectory==true and that folder doesn't exist.

	Else return None.
	'''

	#generate this_months_folder_name
	this_months_folder = f"{year}_{month:02}"

	#first see if it's a new month. if so, make the folder if desired
	abs_path_of_this_months_folder = join(exp_data_folder, this_months_folder)
	if not isdir(abs_path_of_this_months_folder):
		if makedirectory==True:
			mkdir(abs_path_of_this_months_folder)
		return None

	#check inside this months folder to find last made folder
	(_,this_months_dirs, _) = next(os.walk(abs_path_of_this_months_folder))

	#find all folders with data
	data_folders = [x for x in this_months_dirs if f"{year}" in x]
	if len(data_folders) != 0:
		#return most recent
		return data_folders[-1]
	else:
		return None

if __name__ == '__main__':
	most_recent_folder = return_months_last_data_folder(now.year,now.month)
	if todays_folder_prefix not in most_recent_folder:
		print(f"Most recent folder is {most_recent_folder}")
		print("Today's Data doesn't have a folder! Not transferring data!")
		# raise Exception("No folder for Today's Data!")


	#path is defined in 'from lyse import *'
	all_lyse_data = data(path)

	with h5py.File(path,'a') as hdf:

		#
		#	Record photon arrivals
		#

		#pull data from hdf
		file_array = np.array(hdf['/data/photon_arrivals/all_arrivals'])
		
		#create rootname
		sequence_and_run_number = os.path.basename(path)
		sequence_and_run_number = sequence_and_run_number[11:]
		sequence_name = sequence_and_run_number[5:-3]
		sequence_name = "GreenProbe_P7888"
		# print(sequence_name)

		#store in experimental data folder	
		data_folder = join(exp_data_folder,this_months_folder,most_recent_folder,"Counter")
		(_,_,all_files) = next(os.walk(data_folder))
		run_number = len(all_files)
		matlab_exp_file_location = join(data_folder,f"{sequence_name}_{run_number:04}.lst")
		file_array.tofile(matlab_exp_file_location)
		
		#
		#	Write Files for MATLAB to analyse.
		#

		ComtecFilesToReadLocation = "\\\\YBMINUTES\\Users\\YbMinutes\\Documents\\Experimental Data\\FolderForFileCommunicationWithYBCLOCK\\ComtecFilesToRead.txt"

		with open(ComtecFilesToReadLocation, 'a') as f:
			f.write(f"{matlab_exp_file_location}\n")

# -*- coding: utf-8 -*-
"""
Created on Mon May 23 11:54:41 2022

@author: gusta
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import h5py
from lyse import *
import matplotlib as mpl
mpl.rcParams['toolbar'] = 'None'

# Import the dictionaries holding the current and optimal parameters
def open_globals(filename):
	#variables for repacking the globals file
	userProfile         = "C:\\Users\\YbClockReloaded"
	filename        = os.path.join(userProfile,f"labscript-suite\\userlib\\labscriptlib\\ybclock\\{filename}.h5")
	# userProfile         = "C:\\Users\\YBWATCH\\Desktop"
	# filename        = os.path.join(userProfile,f"for_gustavo\\for_gustavo\\{filename}.h5")

	globals_dict = {}
	with h5py.File(filename, 'r') as f:
		globals_ = f['globals']
		for group_key in globals_:
			group = globals_[group_key]
			attributes = group.attrs
			globals_dict.update(
					zip(attributes.keys(), attributes.values())
				)
	return globals_dict

def find_number_of_common_keys(dict1, dict2):
	count = 0
	keys = []
	for key in dict1:
		if key in dict2:
			keys.append(key)
			count += 1
	return count, keys

def find_number_of_different_values(optimal_parameter_dict, current_parameter_dict):
	valid_keys = []
	count = 0
	for i, key in enumerate(optimal_parameter_dict.keys()):
		if key in current_parameter_dict.keys():
			try:
				optimal_parameter_dict[key] = float(optimal_parameter_dict[key])
				current_parameter_dict[key] = float(current_parameter_dict[key])

				if np.isscalar(optimal_parameter_dict[key]):
				
					if np.abs(optimal_parameter_dict[key] - current_parameter_dict[key]) > 1e-2:

						valid_keys.append(key)
						count += 1
				else:
					pass
			except:
				import traceback
				import sys
				# traceback.print_exception(*sys.exc_info())
	return count, valid_keys

def filter_dict(mydict, keys):
	return {k:v for k,v in mydict.items() if k in keys}
def setup(ax):
	from matplotlib.ticker import ScalarFormatter, NullFormatter
	#Creating plots that are only 1D
	ax.spines['right'].set_color('none')
	ax.spines['left'].set_color('none')
	ax.yaxis.set_major_locator(ticker.NullLocator())
	ax.spines['top'].set_color('none')
	ax.xaxis.set_ticks_position('bottom')
	ax.tick_params(which='major', width=1.00)
	ax.tick_params(which='major', length=5)
	ax.tick_params(which='minor', width=0.75)
	ax.tick_params(which='minor', length=2.5)
	ax.set_ylim(0, 1)
	ax.patch.set_alpha(0.0)

def main():
	current_run = Run(path)
	optimal_parameter_dict = open_globals("last_known_optimal")
	current_parameter_dict = current_run.get_globals()
	#Graph the optimal and current parameters on a line graph
	num_plots, keys = find_number_of_different_values(optimal_parameter_dict, current_parameter_dict)
	optimal_parameter_dict = filter_dict(optimal_parameter_dict, keys)
	current_parameter_dict = filter_dict(current_parameter_dict, keys)
	import matplotlib as mpl
	mpl.rcParams['toolbar'] = 'None' 
	fig, axs = plt.subplots(num_plots) 
	# fig.tight_layout()
		
	for i, key in enumerate(optimal_parameter_dict.keys()):
		if key in current_parameter_dict.keys():
			optimal_parameter_dict[key] = float(optimal_parameter_dict[key])
			current_parameter_dict[key] = float(current_parameter_dict[key])
			setup(axs[i])

			axs[i].scatter(np.abs(current_parameter_dict[key]/optimal_parameter_dict[key]),0,s = 100, marker = "v")
			axs[i].set_xscale('log')
			axs[i].get_xaxis().set_major_formatter(ticker.ScalarFormatter())
			axs[i].set_xticks([0.5, 1, 2])
			axs[i].set_xlim(1/2,2)
			axs[i].set_xlabel(key)
			
if __name__ == '__main__':
	main()
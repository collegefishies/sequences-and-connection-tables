from lyse import data

import numpy as np
from numpy import array
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
if __name__ == '__main__':
	try:
		df = data(n_sequences=50)
		df = data()
		fig, axs = plt.subplots(3)


		try:
			runtimes	= array(df['run time'])
			sequence_index = array(df['sequence_index'])
			Neta_1   	= array(df['cavity_scan_analysis','Neta_1'])
			Neta_2   	= array(df['cavity_scan_analysis','Neta_2'])
			Neta_3   	= array(df['cavity_scan_analysis','Neta_3'])
			Neta_4   	= array(df['cavity_scan_analysis','Neta_4'])
			# photons	= array(df['cavity_scan_analysis', 'number_of_detected_photons_2'])
			# photons	= array(df['empty_cavity_helper', 'number_of_detected_photons_1'])

			axs[0].scatter(sequence_index,Neta_3 + Neta_4,s=10, label='Neta_3+4')
			axs[0].legend()
			# axs[0].tick_params(axis='y', which='minor')
			# ml = AutoMinorLocator()
			# axs[0].yaxis.set_minor_locator(ml)
			axs[0].grid()
			axs[0].set_ylabel('Neta')
			axs[0].set_ylim(bottom=0)
			axs[0].set_xlabel('sequence_index')
		except:
			pass

		try:
			axs[1].set_ylabel('Cost')
			axs[1].grid()
			cost	= array(df['generate_cost','Cost'])
			sequence_index = array(df['sequence_index'])
			axs[1].scatter(sequence_index, cost,s=10, label='Cost')
		except:
			pass

		try:
			runtimes        	= array(df['run time'])
			pumping_fraction	= array(df['measure_sz_over_s','pumping_fraction'])

			axs[2].scatter(sequence_index,pumping_fraction,s=10, label='pumping_fraction')
			axs[2].legend()
			# axs[2].tick_params(axis='y', which='minor')
			# ml = AutoMinorLocator()
			# axs[2].yaxis.set_minor_locator(ml)
			axs[2].grid()
			axs[2].set_ylabel('pumping_fraction')
			axs[2].set_ylim(bottom=0,top=3)
			axs[2].set_xlabel('sequence_index')
		except:
			pass
		print("Done.")
	except Exception as e:
		print(f"Error: {e}")
		import traceback
		import sys
		traceback.print_exception(*sys.exc_info())
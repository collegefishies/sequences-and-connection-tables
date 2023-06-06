from lyse import *
import numpy as np
from numpy import array
import matplotlib.pyplot as plt

ANALYSISMODE = 1
if __name__ == '__main__':
	try:
		df = data()

		vars	= {}
		if ANALYSISMODE == 1:
			parameter_str	= 'blue_mot_duration'
			# mask_str   	= 'use_cooling_pi'


		# vars['Neta_2'] = array(df['atoms_in_cavity_helper','Neta_2'])
		# vars['Neta_3'] = array(df['atoms_in_cavity_helper','Neta_3'])
		vars['Neta_1'] = array(df['generate_cost','Neta'])
		vars[parameter_str] = array(df[parameter_str])
		# vars[mask_str] = list(df[mask_str])
		top = 'Neta_1'
		# bot = 'Neta_2'
		# cooling_efficency = vars[top]/vars[bot]

		# mask = array([1 if x else 1 for x in vars[mask_str]])
		plt.scatter(vars[parameter_str], vars[top],s=10)
		plt.title(f'{top}')
		plt.ylabel('Cost')
		plt.xlabel(parameter_str)
		plt.ylim(0 ,400)
		plt.grid()


		print("Done.")
	except Exception as e:
		print(e)
		pass
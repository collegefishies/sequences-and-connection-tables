from lyse import *
import numpy as np
from numpy import array
import matplotlib.pyplot as plt

if __name__ == '__main__':
	try:
		df = data()

		cost    	= array(df['generate_cost','Neta'])
		runtimes	= array(df['run time'])
		Neta    	= array(df['atoms_in_cavity_helper','Neta_1'])

		fig, ax = plt.subplots()

		ax.scatter(Neta,abs(cost),s=10)
		ax.set_yscale('log')
		ax.set_xscale('log')
		ax.set_ylabel('Cost')
		ax.set_xlabel('Neta')
		ax.grid()

		print("Done.")
	except Exception as e:
		print(e)
		pass
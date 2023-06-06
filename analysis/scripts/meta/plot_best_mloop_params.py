'''
	A script, an attempt at plotting the parameters of the best sequence to understand what the machine is doing.

	When functioning it should be a real number line for each parameter, and a single dot for the parameter.
	Each run can be colorcoded, as well as amplitude coded for how good the cost was. or just color coded for the cost.
'''

from lyse import *
import numpy as np
from numpy import array
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


# Setup a plot such that only the bottom spine is shown
def setup(ax):
	'''source: https://matplotlib.org/2.0.2/examples/ticks_and_spines/tick-locators.html'''
	ax.spines['right'].set_color('none')
	ax.spines['left'].set_color('none')
	ax.yaxis.set_major_locator(ticker.NullLocator())
	ax.spines['top'].set_color('none')
	ax.xaxis.set_ticks_position('bottom')
	ax.tick_params(which='major', width=1.00)
	ax.tick_params(which='major', length=5)
	ax.tick_params(which='minor', width=0.75)
	ax.tick_params(which='minor', length=2.5)
	ax.set_xlim(0, 5)
	ax.set_ylim(0, 1)
	ax.patch.set_alpha(0.0)

if __name__ == '__main__':
	try:
		df = data()
		parameters = ('green_mot_frequency', "lattice_loading_frequency")

		plt.figure(figsize=(8, 6))
		n = 8

		# Linear Locator
		ax = plt.subplot(n, 1, 1)
		setup(ax)
		ax.xaxis.set_major_locator(ticker.LinearLocator(3))
		ax.xaxis.set_minor_locator(ticker.LinearLocator(31))
		ax.text(0.0, 0.1, "LinearLocator(numticks=3)",
				fontsize=14, transform=ax.transAxes)
		plt.scatter( 0.5, 1)
	except Exception as e:
		print(e)
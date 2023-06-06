from lyse import Run, path, data
from pylab import *


'''
Here is the code to call the globals in the analysis.

'''

if __name__ == '__main__':
	run = Run(path)
	data_globals = run.get_globals()

	print(data_globals['exp_cavity_kappa'])

	# run.get_trace(probe_sideband_frequency)
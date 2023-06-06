from lyse import *
import numpy as np

if __name__ == '__main__':
	try:
		run = Run(path)
		squeezing_photons_0 = run.get_result(name ="squeezing_photons_0", group='cavity_photon_count_analysis')
		squeezing_photons_1 = run.get_result(name ="squeezing_photons_1", group='cavity_photon_count_analysis')
		run.save_result(name="squeezing_photon_imbalance", value=squeezing_photons_1 - squeezing_photons_0)	

	except Exception as e:
		print(f"Error: {e}")
		import traceback
		import sys
		traceback.print_exception(*sys.exc_info())
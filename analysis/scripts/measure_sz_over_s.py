'''
	Measures $\frac{S_z}{S}$ by looking at `Neta_3, Neta_4`
	Measure Pumping Fraction
'''
from lyse import path, Run
import numpy as np
from labscriptlib.ybclock.utils import HiddenPrints
import warnings
def main():
	try:
		run = Run(path)
		Neta_1 = run.get_result("cavity_scan_analysis", "Neta_1")
		Neta_2 = run.get_result("cavity_scan_analysis", "Neta_2")
		Neta_3 = run.get_result("cavity_scan_analysis", "Neta_3")
		Neta_4 = run.get_result("cavity_scan_analysis", "Neta_4")
		# Neta_5 = run.get_result("cavity_scan_analysis", "Neta_5")
		# Neta_6 = run.get_result("cavity_scan_analysis", "Neta_6")

		sz = (Neta_3 - Neta_4)/2
		s  = (Neta_4 + Neta_3)/2
		sz_over_s = sz/s
		run.save_result(name="sz_over_s", value=sz_over_s)
		run.save_result(name="pumping_fraction", value = Neta_2/Neta_1)

	except Exception as e:
		import traceback
		import sys
		traceback.print_exception(*sys.exc_info())

def quietMain():
	with warnings.catch_warnings():
		warnings.simplefilter("ignore")
		with HiddenPrints():
			main()

#execute quietMain
if __name__ == '__main__':
	quietMain()
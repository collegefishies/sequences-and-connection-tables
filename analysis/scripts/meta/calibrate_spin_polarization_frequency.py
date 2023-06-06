from lyse import *
import numpy as np
from numpy import array
import matplotlib.pyplot as plt


if __name__ == '__main__':
	try:
		df = data()

		parameter_str = 'calibration_precession_time'
		parameter_str = 'rabi_pulse_duration'
		parameter_str = 'squeezing_light_power'
		parameter_str = 'squeezing_photons'
		parameter_str = 'spin_polarization_power'
		parameter_str = 'spin_polarization_frequency'

		#post select on Neta
		# df = df[df['cavity_scan_analysis', 'Neta_1'] > 700]
		Neta_1   	= array(df['cavity_scan_analysis','Neta_1'])
		Neta_2   	= array(df['cavity_scan_analysis','Neta_2'])
		Neta_3   	= array(df['cavity_scan_analysis','Neta_3'])
		parameter	= array(df[parameter_str])

		plt.scatter(parameter,Neta_2/Neta_1,s=10,label='Neta_2/Neta_1')		
		t = np.linspace(np.min(parameter), np.max(parameter), 1000)
		plt.legend()
		plt.ylabel('')
		plt.xlabel(parameter_str)

		print("Done.")
	except Exception as e:
		print(e)
		pass
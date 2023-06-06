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
		df = df[df['cavity_scan_analysis', 'Neta_1'] > 700]
		Neta_1     	= array(df['cavity_scan_analysis','Neta_1'])
		Neta_2     	= array(df['cavity_scan_analysis','Neta_2'])
		Neta_3     	= array(df['cavity_scan_analysis','Neta_3'])
		# std_dev_1	= array(df['neta_variance_estimator','std_dev_1'])
		# std_dev_2	= array(df['neta_variance_estimator','std_dev_2'])
		# cost     	= array(df['generate_cost','Cost'])
		parameter  	= array(df[parameter_str])
		# fig, ax = plt.subplots()

		# plt.scatter(parameter,cost,s=10,label='Photon Weighted Cavity Scan Variance')
		# plt.scatter(parameter,np.divide(Neta_3,Neta_2),s=10,label='Neta_3/Neta_2')
		plt.scatter(parameter,Neta_2/Neta_1,s=10,label='Neta_2/Neta_1')             		
		# plt.plot(parameter,(std_dev_2/std_dev_1)**2,label='var_2/var_1',alpha=0.2)		
		# plt.plot(parameter,Neta_3/Neta_2,label='Neta_3/Neta_2')
		t = np.linspace(np.min(parameter), np.max(parameter), 1000)
		period = 8.7
		#plt.plot(t,0.5 + 0.4*np.cos(2*np.pi*t/period), label='Fit by Hand $\\left[0.5 + 0.4\\cos(\\frac{2\\pi t}{' +f'{period}' + 'ms})\\right]$')
		# plt.yscale('log')
		plt.legend()
		plt.ylabel('')
		plt.xlabel(parameter_str)
		# plt.ylim([0.8,2.2])
		# ax.set_yscale('log')
		# ax.set_ylabel('Cost')
		# ax.set_xlabel(parameter_str)
		# ax.grid()

		print("Done.")
	except Exception as e:
		print(e)
		pass
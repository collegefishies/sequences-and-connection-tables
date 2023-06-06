'''
	OUTLINE
	Figures out which sequences had the best cost. 
	Bonus Features:
	Updates globals.h5 with the best parameters.
'''


from lyse import *
import numpy as np
from numpy import array
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import os


if __name__ == '__main__':
	try:
		df = data()
		
		# print(df.sort_values('filepath'))
		df = df.sort_values(('generate_cost','Cost'), ascending=False, na_position='last')
		try:
			pass
			# df = df.sort_values(('measure_sz_over_s','pumping_fraction'), ascending=False, na_position='last')
		except:
			print("No Sz over S values")
		# df = df.sort_values(('cavity_scan_analysis','Neta_1'), ascending=False, na_position='last')
		# filepath = df['filepath']
		# cost = np.array(df['generate_cost','Cost'])
		dfopt = df[0:100]

		filepath = dfopt['filepath']
		# cost = np.array(dfopt['generate_cost','Cost'])
		cost = np.array(dfopt['cavity_scan_analysis','Neta_1'])
		
		pumpin_fraction = np.array(dfopt['measure_sz_over_s', 'pumping_fraction'])
		res = '\n'.join(f'{os.path.basename(fname):55}\t\t{cost}\t\t{p_Frac}' for fname,cost,p_Frac in zip(filepath,cost, pumpin_fraction))
		print(res)
		# print(df[0:5])
		# print(os.path.basename(filepath[0]))
	except Exception as e:
		print(e)

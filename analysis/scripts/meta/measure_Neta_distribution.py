from lyse import *
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
def post_select_atom_number(df, atom_number, atom_number_range):
	boolean1 = df['Neta_total'] < atom_number + atom_number_range/2
	boolean2 = df['Neta_total'] > atom_number - atom_number_range/2
	boolean = boolean1 & boolean2
	return df[boolean]
def main():
	df = data(n_sequences=100)
	df = data()
	Neta_3 = array(df['cavity_scan_analysis','Neta_3'])
	Neta_4 = array(df['cavity_scan_analysis','Neta_4'])
	Neta_total = Neta_3 + Neta_4
	df['Neta_total'] = Neta_total
	bin_width = 300
	bins	= int(np.nanmax(Neta_total)//(bin_width)) - 1
	plt.hist(Neta_total,bins=bins)
	plt.title(f'Neta Distribution (Neta_3 + Neta_4)\nMean {np.nanmean(Neta_total):.1f}\n Std. Dev. {np.nanstd(Neta_total):.1f}')
	plt.xlabel('Neta')
	plt.ylabel(f'Counts (cts={len(df)})')
	# plt.gca().set_xlim(left=bin_width)
	# plt.gca().set_ylim(top=20)
	print("Done")
	pass
if __name__ == '__main__':
	try:
		main()	
	except:
		import traceback
		import sys
		traceback.print_exception(*sys.exc_info())
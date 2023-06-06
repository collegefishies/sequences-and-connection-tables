'''
	Plot's the Empty Cavity Frequency over Time.

	Currently it changes plot point color depending on the parity of the sequence
	number. This helps keep track of changes to the sequence. This feature is
	kind of useless seeing as with feedback the sequence will change every shot.

'''
from math import pi
from lyse import *
import pickle
import numpy as np
import matplotlib.pyplot as plt


def pull_unitaries(paths):
	from labscriptlib.ybclock.classes.experimental_cavity import ExperimentalCavity
	exp_cavity = ExperimentalCavity()

	all_times    	= []
	all_unitaries	= []
	for path in paths:
		exp_cavity.get_parameters(path=path)
		#get the atom in cavity scans
		atom_scans = exp_cavity.scan_parameters['atoms_in_cavity']

		times_in_seq = []
		unitaries_in_seq = []
		for scan in atom_scans:
			t      	= scan['t']
			unitary	= scan['unitary']
			if scan['sequence'] == 'calibrate_larmor_frequency':
				times_in_seq.append(t)
				unitaries_in_seq.append(unitary)
		if len(times_in_seq) != 2:
			print(f"Not a valid Larmor Shot: (# Unitaries == {len(times_in_seq)}) != 2")
			continue
		else:
			all_times.append(times_in_seq[1] - times_in_seq[0])
			all_unitaries.append(unitary[1])

	return all_times, all_unitaries

def calculate_mean_spin(unitaries, matrix='sz'):
	initial_state = np.array([0,1])
	means = []
	for U in unitaries:
		if matrix == 'sz':
			sz = initial_state.conj_transpose()*U.hc()*Sx*U*initial_state
			means.append(sz)
	return sz


if __name__ == '__main__':
	#exposes all the variables available in the lyse window
	dataframe = data()


	runtimes = list(dataframe['run time'])
	total_neta = np.array(list(dataframe['atoms_in_cavity_helper','Neta_1']))
	ramsey_neta = np.array(list(dataframe['atoms_in_cavity_helper','Neta_2']))
	precession_time = np.array(list(dataframe['calibration_precession_time']))

	paths = list(dataframe['filepath'])
	# frequencies = list(dataframe['empty_cavity_helper','fcavity_1'])
	#this is what we call the run number. we'll use it to change the color, so we can tell when we changed the sequence.
	sequence_index = list(dataframe['sequence_index'])


	#make some colors.
	cerulean = (4/256,146/256,194/256)
	crimson = (185/256, 14/256, 10/256)
	colors = [cerulean if seq%2 == 0 else crimson for seq in sequence_index]

	#calculate predicted detuning
	times,unitaries = pull_unitaries(paths)
	mean_sz = calculate_mean_spin(unitaries, 'sz')


	expected_detuning = np.arcsin((ramsey_neta - total_neta/2)/total_neta)/precession_time/(2*pi)
	#s - size
	plt.scatter(runtimes, expected_detuning, s=20, c = colors)
	plt.scatter(runtimes, mean_sz, s=20, c = colors)

	plt.title(f"Empty Cavity Frequency (Mean: {np.mean(expected_detuning):.1f})")
	plt.ylabel("Frequency (Hz)")
	plt.xlabel("Time")
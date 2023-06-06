'''
	
	Just prints the spin unitaries held inside the sequence. See
	`experimental_cavity.scan` function for details. The spin unitaries
	are saved as `params`. Parameters are saved in `shot_properties`.


'''
from lyse import *
#Add in libraries for working with HDF files
from labscriptlib.ybclock.classes.experimental_cavity import ExperimentalCavity
import labscript_utils.h5_lock
import h5py
#analysis libs
import numpy as np



if __name__ == '__main__':
	#get all atom unitaries 
	#they're stored in shot_properties/exp_cavity_scan_parameters
	#but luckyily ExperimentalCavity() does this for us.
	exp_cavity = ExperimentalCavity()
	exp_cavity.get_parameters(path=path)

	#get the atom in cavity scans
	atom_scans = exp_cavity.scan_parameters['atoms_in_cavity']

	for scan in atom_scans:
		t      	= scan['t']
		unitary	= scan['unitary']
		print(f"Time: {t}\n Unitary: {unitary}")

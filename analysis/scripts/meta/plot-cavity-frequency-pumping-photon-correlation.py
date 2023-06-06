'''

	Loops through the parameters saved by ExperimentalCavity() class and
	performs analysis by passing the 3 parameters needed to an analysis function.

'''
from lyse import *
from pylab import *

#Add in libraries for working with HDF files
import labscript_utils.h5_lock
import h5py

#Add class
from labscriptlib.ybclock.classes import ExperimentalCavity

#analysis libs
import numpy as np
import matplotlib.pyplot as plt
import labscriptlib.ybclock.analysis.functions.fit_functions as fit_functions
from labscriptlib.ybclock.analysis.functions.empty_cavity_helper import empty_cavity_analysis
from labscriptlib.ybclock.analysis.functions.atoms_in_cavity_helper import atom_cavity_analysis
from labscriptlib.ybclock.analysis.functions.cavity_analysis_lib import *

import pickle
import time

def main():
    #get the pandas dataframe
    df = data()
    photons, cavity_frequencies = extract_photons_and_cavity_frequencies(df)
    #plot the cavity frequency data vs the photon number
    plt.scatter(photons,cavity_frequencies)
    plt.xlabel("Photons")
    plt.ylabel("Cavity Frequency (MHz)")




def extract_photons_and_cavity_frequencies(df):
    #get the photon number 
    photons = df['cavity_photon_count_analysis','pump_photons_0']

    #get the cavity frequency data
    cavity_frequencies = df['empty_cavity_helper','fcavity_1']
    return photons,cavity_frequencies

if __name__ == '__main__':
	main()
from labscriptlib.ybclock.analysis.functions import fit_functions
import numpy as np
import matplotlib.pyplot as plt
from labscriptlib.ybclock.analysis.functions.metadata import extract_sequence_repetition_numbers, extract_date,extract_sequence_name
from lyse import Run

def ringdown_cavity_analysis(data, scan_parameters, path):
	'''

	Here we plot and analyze ringdown measurements.


	'''
	us = 1e-6
	ms = 1e-3
	kHz = 1e3

	for params in scan_parameters:
		# params is a dictionary whose properties are defined in exp_cavity.py
		start_time	= params['t_ringdown_start']
		end_time  	= start_time + params['duration'] + 0.5*ms
		light_f   	= params['light_frequency']

		#Select photons in the scan range
		photons_in_scan_time = data[(data > start_time) & (data < end_time)]-start_time
                        
		print(f"Settings: {params['t']}")
		#Fit the Data using both least_square method and MLE method.	
		# if len(photon_arrivals_in_frequency_MHz) > 200:
		#	#Fit the Data using the least_square method.
		#	try:
		#		best_param_lstsq = fit_functions.fit_rabi_splitting_transmission(
		#			data = photon_arrivals_in_frequency_MHz,
		#			path = path
		#			)
		#		print(best_param_lstsq)
		#	except:
		#		print("least square Photon Arrival Time Fit Failed.")
		# else:
		#	try:
		#		best_param = fit_functions.fit_rabi_splitting_transmission_MLE(
		#			data=photon_arrivals_in_frequency_MHz, 
		#			bnds={"fatom_range":(15,30), "fcavity_range":(15,30), "Neta_range":(0,10000)},
		#			path=path
		#		)
		#		print(best_param)
		#	except:
		#		print("MLE Photon Arrival Time Fit Failed.")

		#Plot
		#Plot
		#Plot

		#extract metadata
		(sequence_number, repetition_number)	= extract_sequence_repetition_numbers(path)
		date                                	= extract_date(path)
		sequence_name                       	= extract_sequence_name(path)
		
		run=Run(path)
		data_globals = run.get_globals()

		#plot data, arrival time in ms
		histogram_resolution = .01;

		n = plt.hist(
			photons_in_scan_time*1000,
			bins=np.arange(0,(end_time-start_time)*1000, histogram_resolution),
			align='mid'
		 )
		
		#decorate plot
		plt.title(f"({date}) #{sequence_number}_r{repetition_number}\n{sequence_name}")
		plt.ylabel("Photon Counts, (0.2 us)")
		plt.xlabel("time")
		
		#plot fit
		# try:
		#	x = np.arange(data_globals["empty_cavity_frequency_sweep_initial"],data_globals["empty_cavity_frequency_sweep_range"], histogram_resolution/3)
		#	y = fit_functions.rabi_splitting_transmission(
		#	                         		f = x,
		#	                         		fatom = best_param_lstsq["fatom"],
		#	                         		fcavity = best_param_lstsq["fcavity"],
		#	                         		Neta = best_param_lstsq["Neta"],
		#	                         		gamma = best_param_lstsq["gamma"],
		#	                         		kappa = best_param_lstsq["kappa"]
		#	                         	)
		#	plt.plot(x,2*max(n[0])*y)		
		# except:
		#	print("Failed plotting fit!")
		# try:
		#	x = np.arange(data_globals["empty_cavity_frequency_sweep_initial"],data_globals["empty_cavity_frequency_sweep_range"], histogram_resolution/3)
		#	y = fit_functions.rabi_splitting_transmission(
		#			f = x,
		#			fatom = best_param["fatom"],
		#			fcavity = best_param["fcavity"],
		#			Neta = best_param["Neta"],
		#			gamma = best_param["gamma"],
		#			kappa = best_param["kappa"]
		#		)
		#	plt.plot(x,2*max(n[0])*y) # I need to scale automatically the amplitude of the signal. Multiply by the max histogram value.
		# except:
		#	print("Failed plotting MLE fit!")
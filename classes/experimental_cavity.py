'''
	Holds functions for performing cavity scans and saving data.
'''
from labscript import compiler, add_time_marker
import labscript_utils.h5_lock
import h5py
import pickle
import numpy as np

class ExperimentalCavity:
	'''
	Records parameters and saves them after each scan call.

	This makes it easier to save and keep track of parameters for simpler analysis.

	`ExperimentalCavity.scan(t, label)` is useful for scanning the cavity.

	`ExperimentalCavity.save_parameters()` is how we record the data to the HDF
	file, currently `.scan()` is using at the end of ever call. A more efficient
	practice might be devised but this will most definitely work for now.


	'''
	scan_parameters = {}
	ringdown_parameters = {}
	number_of_p7888_start_triggers = None

	def __init__(self):
		''' Try to create the metadata group if it doesn't exist. 
		Clear the scan_parameters dict, as it seems to stay full after each shot compilation.
		We need to keep track of the number of p7888 pulses sent so we know which ones, are spaced at 
		strange intervals. This special pulse number is recorded as a parameter in `scan_parameters`.

		Also tell the P7888 BLACS tab that we're going to need the photon counter.
		This will be done by defining a variable in the HDF file, if it exists we
		are, if not, skip saving data with the photon counter. This will save time
		as currently, in it's inefficient implementation, the P7888 BLACS tab takes
		at least 2 seconds to run.

		'''
		self.scan_parameters = {}
		self.number_of_p7888_start_triggers = 0
		compiler.shot_properties["is_P7888_used"] = True


	def save_parameters(self):
		''' Pickle Parameters then Save to HDF.
		We save to shot_properties so repetitions copy the dict.
		Returns True if it saved. False if not.
		This is designed to only work in runmanager
		'''

		if compiler.hdf5_filename != None:
			pickled_dict = pickle.dumps(self.scan_parameters)
			compiler.shot_properties["exp_cavity_scan_parameters"] = np.void(pickled_dict)
			return True
		else:
			return False
			print("Can't save the parameters!")

	def get_parameters(self,path=None):
		''' Load from HDF file then Unpickle. Intended to work only in analysis.
		This is important as the data will only be saved after the shot has been
		compiled.'''
		
		if compiler.hdf5_filename != None:
			#exit from the function as this is is only supposed to be used in lyse.
			return None
		else:
			#we'll assume it's being used in lyse.
			hdf5_filename = path

		with h5py.File(hdf5_filename, 'r') as hdf5_file:
			grp = hdf5_file['/shot_properties']
			void_pickled_dict = grp.attrs["exp_cavity_scan_parameters"]
			pickled_dict = void_pickled_dict.tobytes()
			self.scan_parameters = pickle.loads(pickled_dict)
		return self.scan_parameters

	def pulse_p7888_start_trigger(self, t):
		'''
			This function sends a TTL pulse of 1ms duration to the photon counter.
			It also keeps track of how many pulses we've sent for easier analysis.
		'''
		us = 1e-6
		ms = 1e-3

		p7888_start_trigger.enable(t)
		p7888_start_trigger.disable(t + 500*us)

		self.number_of_p7888_start_triggers += 1
		return 1*ms

	def scan(self,t, label, params={}, add_markers=False):
		'''

		t     	- scan light across the cavity at time t.
		label 	- name of the cavity scan you are performing.
		params	- add any extra parameters you wish to save in the HDF file.
		add_markers - adds time markers and the beginning of  each scan.
		
		This function turns on the light for the experimental cavity `shutter_open_time`
		before the scan time `t`.

		The label will be used for analysis and grouping parameters together. The
		label should be identical if you are using it for the same purpose. This
		makes it easier for the analysis code to partition the shots.

		'''
		ms = 1e-3
		us = 1e-6
		t0 = t

		shutter_open_time = 5*ms

		#make room in the dictionary if this label is used for the first time.
		self.scan_parameters.setdefault(label, [])

		#calculate the parameters from globals
		duration  	= empty_cavity_sweep_duration*ms
		initial_f 	= empty_cavity_frequency_sweep_initial
		final_f   	= empty_cavity_frequency_sweep_initial+empty_cavity_frequency_sweep_range
		samplerate	= empty_cavity_samples/(empty_cavity_sweep_duration*ms)

		parameters = {
			"t"                    	: t,
			"duration"             	: duration,
			"initial_f"            	: initial_f,
			"final_f"              	: final_f,
			"samplerate"           	: samplerate,
			"initial_start_trigger"	: self.number_of_p7888_start_triggers
		}

		for key,value in params.items():
			if key in parameters:
				raise Exception(f"Error: Do not use the key '{key}'. It exists in the parameters to be saved already.")
			else:
				parameters[key] = value

		#record the parameters in a dictionary inside a list that holds dictionarys.
		self.scan_parameters[label].append(parameters)

		#initial laser light management
		if add_markers: add_time_marker(t - shutter_open_time ,f"Cavity Scan Prep: {label}")

		#set sideband frequency before turning on power
		green.probe.frequency.constant(t - shutter_open_time/10, value=initial_f, units='MHz')
		green.probe.intensity.constant(t,value=exp_cavity_scan_power, overload=True)

		photon_counter_shutter.enable(t - shutter_open_time)	#open photon counter shutter

		tloop = t

		#update scan time to be right when the frequency scans
		self.scan_parameters[label][-1]['t'] = t
		#tell labscript to perform the scan with the given parameters.
		t += green.probe.frequency.ramp(
			t, 
			duration=duration,
			initial=initial_f,
			final=final_f,
			samplerate=samplerate, units="MHz"
		)

		#run the photon counter
		while tloop < t:
			tloop += self.pulse_p7888_start_trigger(tloop)
			

		#turn off lights
		t += green.probe.turnoff(t, warmup_value=0)
		# photon_counter_shutter.disable(t)
		#close photon counter shutter

		self.save_parameters()

		#remove the shutter turn off time (shutter_open_time) in case we want to loop.
		#this will prevent unneccessary shutter pulses
		return t-t0

	def count_photons(self,t,label,duration, add_markers=False):
		'''
			Opens the Shutter to the P7888 Photon Counter but doesn't actually scan the frequency of the green. Useful for counting photons transmitted through the cavity.
		'''
		ms = 1e-3
		us = 1e-6
		t0 = t

		shutter_open_time = 5*ms

		#make room in the dictionary if this label is used for the first time.
		self.scan_parameters.setdefault(label, [])

		#record the parameters in a dictionary inside a list that holds dictionarys.
		self.scan_parameters[label].append({
			"t"                    	: t,
			"duration"             	: duration,
			"initial_start_trigger"	: self.number_of_p7888_start_triggers
		})

		#initial laser light management
		if add_markers: add_time_marker(t - shutter_open_time ,f"Cavity Photon Count Prep: {label}")

		photon_counter_shutter.enable(t - shutter_open_time)	#open photon counter shutter

		tloop = t

		#update scan time to be right when the photons start getting counted
		self.scan_parameters[label][-1]['t'] = t

		#run the photon counter
		while tloop < t + duration:
			tloop += self.pulse_p7888_start_trigger(tloop)
		t = tloop

		# photon_counter_shutter.disable(t)	
		#close photon counter shutter
		t += shutter_open_time

		self.save_parameters()

		#remove the shutter turn off time (shutter_open_time) in case we want to loop.
		#this will prevent unneccessary shutter pulses
		return t-t0

	def ringdown(self,t, label, params={}, add_markers=True, DEBUG = False):
		'''

		params	- add any extra parameters you wish to save in the HDF file.
		
		Cavity ringdown measurement.

		'''
		ms = 1e-3
		us = 1e-6
		t0 = t

		shutter_open_time = 5*ms

		#make room in the dictionary if this label is used for the first time.
		self.scan_parameters.setdefault(label, [])

		#calculate the parameters from globals
		buildup_time 	= buildup_duration*us
		ringdown_time	= ringdown_duration*us
		laser_f      	= exp_cavity_set_frequency

		#record the parameters in a dictionary inside a list that holds dictionarys.
		self.scan_parameters[label].append({
			"t"               	: t,
			't_ringdown_start'	: t+buildup_time,
			"duration"        	: ringdown_time,
			"light_frequency" : laser_f,
			"initial_start_trigger"	: self.number_of_p7888_start_triggers
		})

		#initial laser light management
		if add_markers: add_time_marker(t - shutter_open_time ,f"Cavity Photon Count Prep: {label}")

		photon_counter_shutter.enable(t - shutter_open_time)	#open photon counter shutter
		#set sideband frequency before turning on power
		green.probe.frequency.constant(t - shutter_open_time/10, value=laser_f, units='MHz')
		green.probe.intensity.constant(t - shutter_open_time/10,value=ringdown_cavity_power, overload=True)

		tloop = t

		t += buildup_time
		green.probe.intensity.constant(t, value = 0, overload=True)

		

		#run the photon counter
		print(f"Time at First Pulse: {tloop}")
		if DEBUG:
			while tloop < t + buildup_time+ringdown_time + 1*ms:
				tloop += self.pulse_p7888_start_trigger(tloop)
			t = tloop
		else:
			tloop = t
			while tloop < t + ringdown_time + 1.*ms:
				tloop += self.pulse_p7888_start_trigger(tloop)
			t = tloop

		self.save_parameters()

		t += 10*ms
		#remove the shutter turn off time (shutter_open_time) in case we want to loop.
		#this will prevent unneccessary shutter pulses
		t += green.probe.turnoff(t, warmup_value=0)
		return t-t0

def ringdown_Delete(self,t, label, params={}, add_markers=True):
		'''

		params	- add any extra parameters you wish to save in the HDF file.
		
		Cavity ringdown measurement.

		'''
		ms = 1e-3
		us = 1e-6
		t0 = t

		shutter_open_time = 5*ms

		#make room in the dictionary if this label is used for the first time.
		self.ringdown_parameters.setdefault(label, [])

		#calculate the parameters from globals
		buildup_time 	= buildup_duration*us
		ringdown_time	= ringdown_duration*us
		laser_f      	= exp_cavity_set_frequency

		parameters = {
			't_ringdown_start' 	: t0+buildup_time,
			"duration"	: ringdown_time,
			"light_frequency" : laser_f,
			"initial_start_trigger"	: self.number_of_p7888_start_triggers
		}

		for key,value in params.items():
			if key in parameters:
				raise Exception(f"Error: Do not use the key '{key}'. It exists in the parameters to be saved already.")
			else:
				parameters[key] = value

		#record the parameters in a dictionary inside a list that holds dictionarys.
		self.ringdown_parameters[label].append(parameters)

		#initial laser light management
		if add_markers: add_time_marker(t - shutter_open_time ,f"Cavity Ringdown Prep: {label}")

		#set sideband frequency before turning on power
		green.probe.frequency.constant(t - shutter_open_time/10, value=laser_f, units='MHz')
		green.probe.intensity.constant(t,value=ringdown_cavity_power, overload=True)

		photon_counter_shutter.enable(t - shutter_open_time)	#open photon counter shutter

		tloop = t-1*ms		
		
		#update scan time to be right when the photons start getting counted
		self.ringdown_parameters[label][-1]['t'] = t
		
		#turn off lights
		t += green.probe.turnoff(t+buildup_time, warmup_value=0)
		# photon_counter_shutter.disable(t)
		#close photon counter shutter

		#run the photon counter
		while tloop < t + ringdown_time + 1*ms :
			tloop += self.pulse_p7888_start_trigger(tloop)
		t = tloop

		self.save_parameters()

		#remove the shutter turn off time (shutter_open_time) in case we want to loop.
		#this will prevent unneccessary shutter pulses
		return t-t0

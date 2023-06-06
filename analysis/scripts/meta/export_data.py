from lyse import *
import os

root = 'C:/Users/YbClockReloaded/Downloads/'

def export_data(file, data):
	import json
	file = os.path.join(root, file)
	with open(file,'w') as f:
		json.dump(
			data,
			f,
			indent=4,
		)
	print(f"Data saved in {file}")

def extract_photon_frequencies_data():
	from labscriptlib.ybclock.classes import ExperimentalCavity
	from labscriptlib.ybclock.analysis.functions.cavity_analysis_lib import parse_scan_parameters
	from labscriptlib.ybclock.analysis.functions.cavity_analysis_lib import select_photons_in_scan
	from labscriptlib.ybclock.analysis.functions.cavity_analysis_lib import convert_arrival_time_to_frequency
	df = data()
	filepaths = df['filepath']
	data_to_save = []
	for path in filepaths:
		run = Run(path)
		#EXTRACT CAVITY SCAN PARAMETERS METADATA
		exp_cavity = ExperimentalCavity()
		cavity_scan_parameters = exp_cavity.get_parameters(path)
		#EXTRACT PHOTON DATA
		photon_arrival_times = run.get_result_array(
				group='extract_photon_arrival_times',
				name='processed_arrivals_ch_1'
			)
		for a_scan in cavity_scan_parameters['atoms_in_cavity']:
			start_time, end_time, final_f, initial_f = parse_scan_parameters(a_scan)
			scan_photons, _ = select_photons_in_scan(
				photon_arrival_times=photon_arrival_times,
				start_time=start_time,
				end_time=end_time
				)
			photon_frequencies = convert_arrival_time_to_frequency(
					photon_arrival_times=scan_photons,
					initial_f=initial_f,
					final_f=final_f,
					start_time=start_time,
					end_time=end_time,
				)
			data_to_save.append(list(photon_frequencies))
	return data_to_save

def save_photon_data():
	data = extract_photon_frequencies_data()
	export_data('photon_frequencies.json', data)
if __name__ == '__main__':
	save_photon_data()
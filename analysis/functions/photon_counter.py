'''
	(c) Enrique Mendez, 2020

	Contains functions for helping with extracting data from the Photon Counting
	cards produced .LST files. Extracted from my old work on the blacs_worker.py
	in the P7888 device in user_devices.
'''
import numpy as np
from labscriptlib.ybclock.classes import ExperimentalCavity

DEBUG = True
def determine_newline_type(entire_file):
	'''newline_type, newline = determine_newline_type(entire_file)

	Reads a whole file in as a string and returns newline type as string 'CRLF',
	'CR', 'LF' as well as the newline string.
	'''
	if(b'\r\n' in entire_file):
		if DEBUG: print("Contains CRLF")
		newline_type = 'CRLF'
		newline = b'\r\n'
	elif(b'\r' in entire_file):
		if DEBUG: print("Contains CR")
		newline_type = 'CR'
		newline = b'\r'
	elif(b'\n' in entire_file):
		if DEBUG: print("Contains LF")
		newline_type = 'LF'
		newline = b'\n'

	return (newline_type, newline)

def split_file_into_header_and_data(entire_file, newline):
	''' header, data = split_file_into_header_and_data(entire_file, newline) 

	entire_file is a binary string.

	Reads entire file to find the start of the data '[DATA]' and
	then looks a newline after it to find the datastream.
	'''

	#find the start of the data and split the .lst file
	data_marker = entire_file.find(b'[DATA]')
	data_start = data_marker + len(b'[DATA]') + len(newline)
	header = entire_file[0:data_start]
	data = entire_file[data_start:]

	return header, data

def decode_data(data,verbose=False):
	''' channels, quantized_times = decode_data(data)
	
	data is a binary string.

	Deconverts the bytes into python-computable integer lists. Data is encoded 
	as a LSB first and as decoded as such.

	Channel Values are from 0 to 3 inclusive. Denoting the 4 input channels.
	The Start events are encoded in one of these channels, and denoted by
	the 0 timing and non-zero channel.

	Quantized times are in units found in the header file.

	Verbose print's the decoded data in binary format.
	'''

	if verbose:
		for char in data:
			print(char)
	if len(data) % 4 != 0:
		#raise RuntimeError(f"Error: P7888 data isn't in 32 bit chunks.\n len(data)=4*({len(data)//4})+{len(data)%4}")
		if DEBUG: print(f"Warning: P7888 data isn't in 32 bit chunks.\n len(data)=4*({len(data)//4})+{len(data)%4}")
		if DEBUG: print(f"Truncating data to be in 32 bit chunks.")
		# if not DEBUG: print(f"Length of Data is {4*(len(data)//4)}")
		data = data[0:(len(data)//4)*4]


	number_of_32_bit_chunks = len(data)//4

	#datalines breaks up the data string 'line' by 'line'. A 'line' is defined to be a 32-bit chunk.
	datalines	= [None] * number_of_32_bit_chunks
	dataints 	= np.zeros(number_of_32_bit_chunks, dtype=np.int64)

	for i in range(number_of_32_bit_chunks):
		datalines[i]	= data[4*i:4*(i+1)]
		dataints[i] 	= int.from_bytes(datalines[i], byteorder='little')

	#seperate the first four bits (data is now in Most Significant Bit First).
	channels       	= np.zeros(number_of_32_bit_chunks, dtype=np.int32)
	quantized_times	= np.zeros(number_of_32_bit_chunks, dtype=np.int32)

	for i in range(number_of_32_bit_chunks):
		channels[i]       	= dataints[i] >> 30	
		quantized_times[i]	= (0xffFFffFF >> 2) & dataints[i]
		if verbose:
			print("0b{:02b}:{:030b}".format(channels[i],quantized_times[i]))

	return channels, quantized_times

def decode_header(header, verbose=False):
	''' dictionary = decode_header(header)

	header is binary string.

	Takes the header datastream and splits it into keys and values in
	dictionary.

	All values are strings.

	'''

	dictionary = {}

	header = header.decode('utf-8')	#convert bytestream to string
	header = header.splitlines()   	#break up into line by line.


	#remove the datafile timestamp before extracting keys and values.
	dictionary['timestamp'] = header.pop(0)
	#remove the useless '[DATA]' line
	header.pop()
	if verbose: print(header)

	for line in header:
		if line[0] == ';':
			#skip commented lines.
			continue
		if '=' in line:
			split_line = line.split('=')
		else:
			split_line = line.split(':')

		#strip removes leading and trailing whitespace.
		dictionary[split_line[0]] = split_line[1].strip()

	if verbose:
		print(dictionary)
	
	return dictionary

def convert_to_absolute_time(t0, channels, quantized_times, start_trigger_period, quantized_time_unit,path):
	'''
	Returns a 2D list, for each channel, returns the absolute arrival times of every photon.

	'''

	#initialize list that holds quantities
	number_of_channels = 4
	arrival_times = [None]*number_of_channels
	for i in range(number_of_channels):
		arrival_times[i] = []

	#check to see if lengths match.
	if len(channels) != len(quantized_times):
		print("Error: len(channels) != len(quantized_times)")
		return

	#extract cavity scan times from ExperimentalCavity class.
	exp_cavity = ExperimentalCavity()
	cavity_scan_parameters = exp_cavity.get_parameters(path)

	all_scan_dicts = []
	for each_scan_type in cavity_scan_parameters.keys():
		all_scan_dicts += cavity_scan_parameters[each_scan_type]

	absolute_time_of_each_scan_start_trigger = {}
	for each_scan in all_scan_dicts:
		# print(each_scan)
		absolute_time_of_each_scan_start_trigger[each_scan['initial_start_trigger']] = each_scan['t']

	# print(absolute_time_of_each_scan_start_trigger)

	#scan through photon counts and calculate absolute arrival times
	t = t0
	start_triggers = 0
	for i in range(len(quantized_times)):
		#find start trigger then increment time
		if (channels[i] == 3) and (quantized_times[i] == 0):
			#we've found a start trigger
			if start_triggers in absolute_time_of_each_scan_start_trigger:
				#hop the time because we've the start of a scan.
				t = absolute_time_of_each_scan_start_trigger[start_triggers]
				# print(f"Cavity_Scan_Time: {t}")
			else:
				#we are mid scan so go up by a 1ms.
				t += start_trigger_period #make sure dt = 0 after the first start trigger.
			start_triggers += 1
			

		#calculate single photon absolute arrival time
		arrival_times[channels[i]].append(
				t + quantized_time_unit*quantized_times[i]
			)

	return arrival_times
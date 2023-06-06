from labscript import add_time_marker

def flush_p7888(t):
	'''
	
	Sends out sequence of pulses to fill up some buffer that the P7888 sends data
	to. The hypothesis, is that the data in the buffer is inaccessible until
	completely filled. This is ran at the end of the experiment to fill that buffer
	to ensure each shot gets a complete data set.

	This operation overfills a buffer leading some spill over into the chunk of
	data the next sequence will read. So it's necessary to have some method to
	discriminate what is data and what is buffer filler. There exists simpler
	algorithms. Out of pure laziness, we are simply supporting the old method. This
	old method is documented in the function `encode_run_number_in_p7888_data(t)`
	in this same submodule. See that for more info on the encoding scheme.

	To be clear, the P7888, takes in square pulses, and records their timing.
	During the flushing sequence, we periodically, at 1ms intervals, send in a 
	`Start Trigger` pulse.

	At the same time, and with disregard to long term synchronization to the start
	triggers. We just send in `flushing photons` at 500kHz rate, or with a period
	of 2us. 

	'''

	flushing_cycles = 50
	start_trigger_period   	= 1e-3
	flushing_time          	= start_trigger_period*flushing_cycles
	flushing_trigger_period	= 2e-6
	number_of_photons      	= int(start_trigger_period/flushing_trigger_period)

	t_loop = t

	for flushing_cycle in range(flushing_cycles):
		#send the start pulse.
		p7888_start_trigger.enable(t_loop)
		p7888_start_trigger.disable(t_loop + start_trigger_period/2)

		t_mini_loop = t_loop
		for bit in range(number_of_photons):
			p7888_flushing_trigger.enable(t_mini_loop)
			p7888_flushing_trigger.disable(t_mini_loop + flushing_trigger_period/2)
			t_mini_loop += flushing_trigger_period
		t_loop += start_trigger_period
	pass

def encode_run_number_in_p7888_data(t, run_number):
	'''
	This function was written to support some old idiosyncracies with the p7888.
	It is not the most optimal method. See `flush_p7888(t)` in this submodule for
	elaboration.

	This subsequence is ran at the beginning of the sequence.

	**Old Method:** Chi's Sequence Number Encoder Method.

	The goal here is to encode the sequence run number into the data. This poses
	some difficulties for us, as I'm not sure labscript has an easy way to keep
	track of the run number without resort to a helper.

	After one start trigger, we send in a series of pulses
	that encode the sequence number in whether or not they arrive. In addition we
	also send in padding photons. These are always at the beginning and end. These
	photons come in at a 2us period and are defined to be `flushing photons` or
	`pulses`. These `flushing photons` are sent in least significant byte first
	(ignoring the padding). 

	More explicitly, let's say our sequence number was 4. Then at times **t** we
	either send a photon (i.e., a 1) or we don't (i.e., a 0). If we write their
	arrival times as 

	Arrival Times (in microseconds)	are	[10,	12,        	...	48, 	50]
	Photons we send                	are	[1, 	LSB,       	...	MSB,	1]
	For four, the ones we send     	are	[1, 	0, 0, 1, 0,	...	0,  	1]
	
	where LSB and MSB are least significant bye and most significant byte
	respectively.
	
	returns the time after encoding has been sent.
	'''

	number_of_encodeable_bits = len(range(10, 52, 2)) - 2 #see docstring.

	if run_number >= 2**number_of_encodeable_bits:
		raise RuntimeError("P7888 Encoder Error: Run Number is too large.")
	if run_number < 0 or not is_integer(run_number):
		raise RuntimeError("P7888 Encoder Error: Invalid run_number.")


	start_trigger_period   	= 1e-3
	flushing_trigger_period	= 2e-6

	#send the start pulse.
	p7888_start_trigger.enable(t)
	p7888_start_trigger.disable(t + start_trigger_period/2)

	#send the encoded bits
	tminiloop = t + 10e-6
	#send in first padding photon
	p7888_flushing_trigger.enable(tminiloop)
	p7888_flushing_trigger.disable(tminiloop + flushing_trigger_period/2)
	tminiloop += flushing_trigger_period
	#send in the sequence number, LSB first.
	for encodeable_bit in range(number_of_encodeable_bits):
		bit = (1 << encodeable_bit & run_number)
		if bit == 1:
			p7888_flushing_trigger.enable(tminiloop)
			p7888_flushing_trigger.disable(tminiloop + flushing_trigger_period/2)
		tminiloop += flushing_trigger_period

	#send in last padding photon
	p7888_flushing_trigger.enable(tminiloop)
	p7888_flushing_trigger.disable(tminiloop + flushing_trigger_period/2)
	tminiloop += flushing_trigger_period

	t += tminiloop
	return t



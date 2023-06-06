
def extract_sequence_repetition_numbers(filepath):
	split_filepath = filepath.split('\\')
	filename = split_filepath[-1]
	split_filename = filename.split('_')
	rep = 0
	seq = int(split_filename[1])
	rep = split_filename[-1]
	if rep.find('rep') == -1:
		rep = 0
	else:
		rep = int(rep[3:-3])
	# print(f"{seq}/{rep}")
	return (seq, rep)
def extract_date(filepath):
	split_filepath = filepath.split('\\')
	filename = split_filepath[-1]
	split_filename = filename.split('_')
	date = split_filename[0]

	return date

def extract_sequence_name(filepath):
	split_filepath = filepath.split('\\')
	filename = split_filepath[-1]
	seq_name = filename[16:]
	seq_name = seq_name[:seq_name.find("_0")]
	return seq_name
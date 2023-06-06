import numpy as np
def drop_nans(*args):
	zipped_tuple = list(zip(*args))
	new_zip = []
	for i in range(len(zipped_tuple)):
		skip = False
		_tuple = zipped_tuple[i]
		for x in _tuple:
			if np.isnan(x):
				skip = True
				break
		if not skip:
			new_zip.append(_tuple)
	return zip(*new_zip)
def drop_infs(*args):
	zipped_tuple = list(zip(*args))
	new_zip = []
	for i in range(len(zipped_tuple)):
		skip = False
		_tuple = zipped_tuple[i]
		for x in _tuple:
			if np.isinf(x):
				skip = True
				break
		if not skip:
			new_zip.append(_tuple)
	return zip(*new_zip)

def drop_nans_and_infs(*args):
	zipped_tuple = list(zip(*args))
	new_zip = []
	for i in range(len(zipped_tuple)):
		skip = False
		_tuple = zipped_tuple[i]
		for x in _tuple:
			if np.isinf(x) or np.isnan(x):
				skip = True
				break
		if not skip:
			new_zip.append(_tuple)
	return zip(*new_zip)
def post_select_atom_number_in_range(df, keys, _min,_max):
	a = 0
	for key in keys:
		a += df[key]
	c1 = a >= _min
	c2 = a <= _max
	c3 = c1 & c2
	return df[c3]
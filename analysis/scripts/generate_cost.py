from lyse import path, Run
import numpy as np
import warnings
from labscriptlib.ybclock.utils import HiddenPrints

PARAMETER_TO_OPTIMIZE = "VARIANCE"



def parameterWeight(x, x_initial,x_final, reward):
	'''
		Returns 1 at x = x_initial, and 10^reward at x=x_final, while being monotonic.
	'''
	xi = x_initial
	exponent = -(x-x_final)**2/(x_final - x_initial)**2 + 1
	return 10**(reward*exponent)

def smartGeometricRoot(x,n):
	'''
		only returns geometric mean if it's `not zero`
	'''
	if x > 1:
		return x**(1/n)
	if x < 1:
		return x

def similarityGaussian(x,y,s=2):
	''' returns 1 if x==y '''
	if x != 0 and y != 0:
		return np.exp(-(x/y-y/x)**2/s**2)
	else:
		return 0

def majorityVoteCost(run,num_scans):
	Neta_list = []
	chi_list = []
	chi_min = 150
	script_name = "cavity_scan_analysis"

	for i in range(num_scans):
		Neta_list.append(run.get_result(script_name,f"Neta_{i+1}"))
		chi_list.append(run.get_result(script_name,f"chi_square_{i+1}"))

	minority_vote =  0

	for i in range(num_scans):
		minority_vote += Neta_list[i]/max(chi_min,chi_list[i])

	majority_vote = 1

	for i in range(num_scans):
		majority_vote *= Neta_list[i]

	return minority_vote + (majority_vote)**(1./num_scans)

def get_scan_results(run, n_max=10):
	photon_number = []
	neta = []
	variance = []

	for i in range(1,n_max):
		try:
			px = run.get_result('cavity_scan_analysis', f'number_of_detected_photons_{i}')
			ne = run.get_result('cavity_scan_analysis', f'Neta_{i}')
			v  = run.get_result('neta_variance_estimator',f'std_dev_{i}')**2

			photon_number.append(px)
			neta.append(ne)
			variance.append(v)
		except:
			break
	return photon_number, neta, variance

def Neta_by_variance_estimate(run):
	photon_number, neta, variance = get_scan_results(run)

	def photon_average(photon_number, x, power=1):
		p = np.power(np.array(photon_number), power)
		x = np.array(x)
		return np.dot(p,x)/np.sum(p)

	if not is_bad_shot(photon_number):
		neta_average = photon_average(photon_number, variance, power=2)
	else:
		neta_average = np.nan
	return neta_average
def twoVoteCost(x,y):
	pass

def is_bad_shot(photon_number):
	if not isinstance(photon_number, list):
		if photon_number < 100:
			return True
	else:
		boolean = False
		for photon_num in photon_number:
			boolean = boolean or (photon_num < 100)
	return False

def tiered_cost(tiers, tier_step=100, bonus=1):
	'''
		`tiers` is a list of tuples [(val, min), (val, min), ...]
		it normalizes the cost to the min desired.
		`tier_step` is the reward for reaching each tier.
	'''
	#produce a tuple of costs that are all of less than one if not satisfied
	#and greater than one if satisfied
	normalized_costs = []
	for i in range(len(tiers)):
		_tuple = tiers[i]
		normalized_cost = _tuple[0]/_tuple[1]
		if i == len(tiers) - 1:
			normalized_costs.append(normalized_cost)
		else:
			normalized_costs.append(normalized_cost)


	cost = 0
	i = 0
	for normalized_cost in normalized_costs:
		if normalized_cost > 1:
			cost += 1
		else:
			if i < len(normalized_costs) - 1:
				cost += normalized_cost
			else:
				cost += normalized_cost * bonus
			return cost*tier_step
		i += 1

	return cost*tier_step

def main():
	try:
		run = Run(path)
		run.set_group('generate_cost')


		if PARAMETER_TO_OPTIMIZE == "GREEN_MOT":
			cost = run.get_result("green_mot_analysis", "green_mot_SNR")
			# err  = run.get_result("mot_analysis", "green_mot_light_err")
			# if np.isnan(err):
			#	cost = np.nan
			run.save_result(name="Cost",value=cost)
		elif PARAMETER_TO_OPTIMIZE == "BLUE_MOT":
			cost = run.get_result("blue_mot_analysis", "blue_mot_SNR")
			run.save_result(name="Cost",value=cost)
		elif PARAMETER_TO_OPTIMIZE == "Neta":
			_globals = run.get_globals()

			if not is_bad_shot(run.get_result('empty_cavity_helper','number_of_detected_photons_1')):
				cost = majorityVoteCost(run,num_scans=3)
				# cost = 300
			else:
				cost = np.nan

			run.save_result(name="Cost", value=cost)	
		elif PARAMETER_TO_OPTIMIZE == 'VARIANCE':
			neta = Neta_by_variance_estimate(run)
			p, n, v = get_scan_results(run)


			neta_desired = 200

			# note the indices start from 0!!!
			cost = tiered_cost(
					[
						(neta, neta_desired),
						(n[2]+n[3], 4000),
						(n[1]/n[2], (10)),
						(similarityGaussian(n[1],n[3]), 0.9),
						(n[3]/n[1], 0.9),
						(n[4]/n[1], 0.9),
						(n[2]+n[3], 8000)
					],
				tier_step = neta_desired
				)
			# note the indices start from 0!!!
			# cost = tiered_cost(
			# 	[
			# 		(neta, neta_desired),
			# 		(n[2]+n[3], 4000),
			# 		(n[1]/n[2], (100000)),
			# 	],
			# tier_step = neta_desired,
			# bonus = 10*100000/neta_desired
			# )
			run.save_result(name="Cost", value=cost)	

	except Exception as e:
		print(f"Error: {e}")
		import traceback
		import sys
		traceback.print_exception(*sys.exc_info())

def quietMain():
	with warnings.catch_warnings():
		warnings.simplefilter("ignore")
		with HiddenPrints():
			main()

if __name__ == '__main__':
	quietMain()
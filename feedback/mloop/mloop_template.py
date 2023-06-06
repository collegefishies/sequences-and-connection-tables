''' 

"M-LOOP takes an object oriented approach to controlling the experiment.
This is different than the functional approach taken by other optimization
packages, like scipy. When using M-LOOP you must make your own class that
inherits from the Interface class in M-LOOP. This class must implement a
method called get_next_cost_dict that takes a set of parameters, runs your
experiment and then returns the appropriate cost and uncertainty."



'''

#Imports for M-LOOP
import mloop.interfaces as mli
import mloop.controllers as mlc
import mloop.visualizations as mlv

#other imports
import numpy as np 
import time

class CustomInterface(mli.Interface):
	''' This interface defines how the MLOOP program will interact with our
	experiment. Usage involves creating an instance: `interface =
	CustomInterface()`, this object is then passed to an mloop controller for
	usage. '''

	def get_next_cost_dict(self, params_dict):
		''' This is the method that runs the experiment given a set of parameters
		and returns the cost of the resultant executed experiment. '''

		return cost_dict

def main():
	''' This is the code that excutes the machine learning online optimization
process (MLOOP). '''
	
	#create the interface
	interface = CustomInterface()
	#create the controller and provide the interface and options
	controller = mlc.create_controller(interface)
	#run the mloop optimization
	controller.optimize()

	#access the optimized parameters (the results will be saved to a file
	#somewhere)
	print(f"Best parameters found: {controller.best_params}")

if __name__ == '__main__':
	main()
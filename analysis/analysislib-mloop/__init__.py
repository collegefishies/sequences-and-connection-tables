'''
	This is the Labscript-MLOOP API. 
		
	#Upgrading this API

	## To Do
	* I wish to rewrite it so it takes in programmatically defined parameters
	instead of resorting to the .ini file.
	
	## How MLOOP interfaces with Python

	It already has an API, so I'm curious what this analysis-mloop api introduces.

	### Native MLOOP API

	One needs to define a Custom Interface and an instance of MLOOP controller.
	Then tells the controller to start.
	
	#### Interface
	The *interface* pulls the cost from the experiment (as every python experiment
	can have a possibly different programming paradigm.)

	#### Controller
	The *controller* is the MLOOP class that does all the looping for you, you need
	to just pass the interface, and the parameters.
	
	The settings sent to the controller actually replaces the .ini file. So why
	did the designed Labscript API rely on it? Dumb design choice.

	
	## How it Works Currently
	### Summary
	  * The `mloop_interface.py` class defines the settings passed to the controller within the class.
	  * The config settings are defined in `LoopInterface.__init__()` inside `mloop_interface.py`.
	  * To change the settings just redefine `self.config = mloop_config.get()`.
	  * I've added a script to change get the config file `ybclock_config.py`. Just change the `get()` call.

	`Taken from https://github.com/rpanderson/analysislib-mloop`
	We use `lyse.routine_storage` to store:

	  * a long-lived thread (`threading.Thread`) to run the main method of `mloop_interface.py` within `mloop_multishot.py`,
	  * a queue (`Queue.Queue`) for `mloop_multishot.py`/`mloop_interface.py` to put/get the latest M-LOOP cost dictionary, and
	  * (when `mock = true`) a variable `x` for `mloop_interface.py`/`mloop_multishot.py` to set/get, for spoofing an `cost_key` that changes with the current value of the (first) M-LOOP optimisation parameter.

	Each time the `mloop_multishot.py` routine runs in lyse, we first check to see if there is an active optimisation by polling the optimisation thread. If it doesn't exist or is not alive, we start a new thread. If there's an optimisation underway, we retrieve the latest cost value from the lyse dataframe (see the `cost_analysis` function) and put it in the `lyse.routine_storage.queue`.

	The `LoopInterface` subclass (of `mloop.interface.Interface`) has a method `get_next_cost_dict`, which:

	  * requests the next experiment shot(s) be compiled and run using `runmanager.remote.set_global()` and `runmanager.remote.engage()`, and
	  * waits for the next cost using a blocking call to `lyse.routine_storage.queue.get()`.

	The main method of `mloop_interface.py` follows the trend of the [M-LOOP » Python controlled experiment tutorial](https://m-loop.readthedocs.io/en/latest/tutorials.html#python-controlled-experiment):

	  * Instantiate `LoopInterface`, an M-LOOP optmiser interface.
	  * Get the current configuration.
	  * Create an `mloop.controllers.Controller` instance for the optimiser interface, using the above configuration.
	  * Run the `optimize` method of this controller.
	  * Return a dictionary of `best_params`, `best_cost`, `best_uncer`, `best_index`.

	Shots are compiled by programmatically interacting with the runmanager GUI. The current value of the optimisation parameters used by M-LOOP are reflected in runmanager, and when a given optimisation is complete, the best parameters are entered into runmanager programmatically.



 '''

from . import *
 
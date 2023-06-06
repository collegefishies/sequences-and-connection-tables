import lyse
from runmanager.remote import set_globals, engage, get_globals
import mloop_config
from mloop.interfaces import Interface
from mloop.controllers import create_controller
import logging
from labscriptlib.ybclock.analysis.scripts import repack_globals
import math


def feedback_exp_cavity():
    import numpy as np
    df = lyse.data()
    actual_cavity_frequency_df = np.array(df['empty_cavity_helper', 'exp_cavity_frequency'])
    actual_cavity_frequency = actual_cavity_frequency_df[-1]

    print("Performing Feedback & Getting Globals...")
    #get PID variables
    retrieved_globals = get_globals()

    G           = retrieved_globals['cavity_frequency_G']
    I           = retrieved_globals['cavity_frequency_I']
    P           = retrieved_globals['cavity_frequency_P']
    integrator  = retrieved_globals['cavity_frequency_integrator']
    _min        = retrieved_globals['min_bridging_frequency_759']
    _max        = retrieved_globals['max_bridging_frequency_759']

    #read desired setpoint
    setpoint    = retrieved_globals['exp_cavity_set_frequency']

    #perform PID
    error = actual_cavity_frequency - setpoint

    output = -G*(P*error)

    #set cavity frequency 
    temp_bridging_frequency = retrieved_globals['bridging_frequency_759']
    temp_bridging_frequency -= output

    if temp_bridging_frequency < _min or temp_bridging_frequency > _max:
        print(f"Warning: Feedback seems out of lock... Near boundarys [{_min},{_max}]")
    elif not math.isnan(temp_bridging_frequency):
        retrieved_globals['bridging_frequency_759'] = temp_bridging_frequency

        #update the global variables
        print("Setting Global Variables...")
        #remote.set_globals(retrieved_globals)


    # repack_globals(["globals","cavity_globals", "optimization"])
    if math.isnan(temp_bridging_frequency):
        return {}
    return {'bridging_frequency_759': temp_bridging_frequency}

logger = logging.getLogger('analysislib_mloop')


def set_globals_mloop(mloop_session=None, mloop_iteration=None):
    """Set globals named 'mloop_session' and 'mloop_iteration'
    based on the current . Defaults are None, which will ideally
    remain that way unless there is an active optimisation underway.
    """
    if mloop_iteration and mloop_session is None:
        _globals = {'mloop_iteration': mloop_iteration}
    else:
        _globals = {'mloop_session': mloop_session, 'mloop_iteration': mloop_iteration}
    try:
        set_globals(_globals)
        logger.debug('mloop_iteration and/or mloop_session set.')
    except ValueError:
        logger.debug('Failed to set mloop_iteration and/or mloop_session.')


class LoopInterface(Interface):
    def __init__(self):
        # Retrieve configuration from file or generate from defaults
        self.config = mloop_config.get()

        # Pass config arguments to parent class's __init__() so that any
        # relevant specified options are applied appropriately.
        super(LoopInterface, self).__init__(**self.config)

        self.num_in_costs = 0

    # Method called by M-LOOP upon each new iteration to determine the cost
    # associated with a given point in the search space
    def get_next_cost_dict(self, params_dict):
        self.num_in_costs += 1
        # Store current parameters to later verify reported cost corresponds to these
        # or so mloop_multishot.py can fake a cost if mock = True
        logger.debug('Storing requested parameters in lyse.routine_storage.')
        lyse.routine_storage.params = params_dict['params']

        if not self.config['mock']:
            logger.info('Requesting next shot from experiment interface...')
            globals_dict = dict(zip(self.config['mloop_params'], params_dict['params']))
            # globals_dict.update(feedback_exp_cavity())
            # feedback_dict = feedback_exp_cavity()
            # globals_dict = feedback_dict.update(globals_dict)
            # print(globals_dict)
            logger.debug('Setting optimization parameter values.')
            set_globals(globals_dict)
            logger.debug('Setting mloop_iteration...')
            set_globals_mloop(mloop_iteration=self.num_in_costs)
            logger.debug('Calling engage().')
            engage()

        # Only proceed once per execution of the mloop_multishot.py routine
        logger.info('Waiting for next cost from lyse queue...')
        cost_dict = lyse.routine_storage.queue.get()
        logger.debug('Got cost_dict from lyse queue: {cost}'.format(cost=cost_dict))
        return cost_dict


def main():
    # Create M-LOOP optmiser interface with desired parameters
    interface = LoopInterface()
    # interface.daemon = True

    # Instantiate experiment controller
    controller = create_controller(interface, **interface.config)

    # Define the M-LOOP session ID and initialise the mloop_iteration
    set_globals_mloop(controller.start_datetime.strftime('%Y%m%dT%H%M%S'), 0)

    # Run the optimiser using the constructed interface
    controller.optimize()

    # Reset the M-LOOP session and index to None
    logger.info('Optimisation ended.')
    set_globals_mloop()

    # Set the optimisation globals to their best results
    logger.info('Setting best parameters in runmanager.')
    globals_dict = dict(zip(interface.config['mloop_params'], controller.best_params))
    set_globals(globals_dict)

    # Return the results in a dictionary
    opt_results = {}
    opt_results['best_params'] = controller.best_params
    opt_results['best_cost'] = controller.best_cost
    opt_results['best_uncer'] = controller.best_uncer
    opt_results['best_index'] = controller.best_index
    return opt_results

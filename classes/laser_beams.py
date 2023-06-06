'''
	Holds the classes for laser light control.

	#Laser Classes

	`Laser()` is just meant to group together `LaserBeam`s as part of the
	datatypes it remembers. `LaserBeam()` is just meant to group together
	frequency and intensity controller classes: `LaserIntensity()` and
	`LaserFrequency()`.
	
	##Desired Example Definitions

	```python

	#define the lasers
	green 	= GreenLaser()
	yellow	= YellowLaser()
	trap  	= TrapLaser()
	```

	##Desired Example Usage
	```python
	#setting the frequency does not automatically turn on the power
	green.probe.frequency.constant(t,'10 Mhz')
	green.probe.turnoff(t)

	#automatically checks to see if laser is off, if so turn on.
	green.probe.intensity.constant(t,'1 mW')
	green.probe.turnoff(t)
	```
'''
import builtins
from labscript.labscript import AnalogQuantity

DEBUG = False
mV = 1e-3
ms = 1e-3

class LaserFrequency(AnalogQuantity):
	'''

		You actually don't need a special class for LaserFrequency. It's just of
		type AnalogQuantity, so just pass the frequency channel to
		`LaserBeam(frequency_control)`.
	
	'''
	pass

class LaserIntensity():
	'''
		
		This is a controller for dealing with the annoying details of turning a
		laser on and off.

		Auto turnoff, turnon features assume sequential usage of the light power
		commands. If you do them out of order, they will not behave correctly. In
		this case, you need to manually set is_on = True/False, or set the overload
		arg to true.

		#To Do

			[x] turnoff function
			[x] turnon function
			[x] constant
			[x] ramp

	'''

	#channels for each of the possible hardware controls
	__intensity_channel = None #AOM/EOM
	__shutter_channel  	= None #Shutter
	__rf_switch_channel	= None #RF Switch

	__turnoff_voltage  	= None #For the AOM/EOM
	__shutter_closetime	= None #Close time from after the TTL is sent
	__shutter_opentime 	= None
	#state variable for keeping track of turning the laser on or off
	is_on = False 

	def __init__(self, 
		intensity_channel=None, 
		shutter_channel=None, 
		turnoff_voltage=None,
		shutter_closetime=None,
		shutter_opentime=None,
		rf_switch_channel=None,
		):

		self.__intensity_channel	= intensity_channel
		self.__shutter_channel  	= shutter_channel
		self.__rf_switch_channel	= rf_switch_channel

		self.__turnoff_voltage  	= turnoff_voltage
		self.__shutter_closetime	= shutter_closetime
		self.__shutter_opentime 	= shutter_opentime

		#determine shutter close time
		if self.__shutter_closetime is None:
			self.__shutter_closetime =	global_shutter_closetime

		if self.__shutter_opentime is None:
			self.__shutter_opentime =	global_shutter_closetime



	def turnoff(self, t, warmup_value, overload=False):
		'''
			Turns off beam if and only if on unless `overload == True` then always turn off.
			`warmup_value` is what value you want for the aom while the shutter is closed.

			#To Do
				[x]	Set up AOM/EOM turn on/off
				[x]	Set up Shutter turn on/off
				[x]	Set up RF Switch turn on/off

		'''

		shutter_closetime = self.__shutter_closetime
		#determine aom/eom turnoff voltage
		if self.__turnoff_voltage is None:
			turnoff_voltage = 0
		else:
			turnoff_voltage = self.__turnoff_voltage





		if self.is_on or overload:
			#turn off aom/eom
			if self.__rf_switch_channel is None:
				self.__intensity_channel.constant(t,value=turnoff_voltage)
			else:
				self.__rf_switch_channel.disable(t)
			
			#close shutter iff we have a shutter
			if self.__shutter_channel is not None:
				self.__shutter_channel.disable(t)

				#turn on  aom/eom iff we have a shutter
				self.__intensity_channel.constant(t + shutter_closetime,value=warmup_value)
				
				if self.__rf_switch_channel is None:
					pass
				else:
					self.__rf_switch_channel.enable(t + shutter_closetime)

			#change on/off status
			self.is_on = False
		return self.__shutter_closetime + self.__shutter_opentime
	def turnon(self, t, *args, overload=False, **kwargs):
		'''
			Turns on beam if and only if off. `*args`, `**kwargs` get passed to the turn on value for the laser.

			## Sequence Turn On Details

			We turn off the beam with the fast control (AOM/EOM) before opening. This
			ensures that the light profile across the atoms is 1) always uniform and 2)
			well controlled in the time domain.

			#To Do
				[x]	Set up AOM/EOM turn on/off
				[x]	Set up Shutter turn on/off
				[x]	Set up RF Switch turn on/off
		'''


		#determine shutter close time
		if self.__shutter_opentime is None:
			shutter_opentime =	global_shutter_closetime
		else:
			shutter_opentime = self.__shutter_opentime
		#determine aom/eom turnoff voltage
		if self.__turnoff_voltage is None:
			turnoff_voltage = 0
		else:
			turnoff_voltage = self.__turnoff_voltage




		if (not self.is_on) or overload:
			#if we have a shutter
			if self.__shutter_channel is not None:
				#turn off beam
				if self.__rf_switch_channel is not None:
					#just turn off the rf switch
					self.__rf_switch_channel.disable(t - shutter_opentime)
				else:
					#turn off the aom/eom
					self.__intensity_channel.constant(t - shutter_opentime,value=turnoff_voltage)

				#open shutter
				self.__shutter_channel.enable(t - shutter_opentime)

			#turn on beam
			if self.__rf_switch_channel is not None:
				#just turn on the rf switch
				self.__rf_switch_channel.enable(t)
			else:
				#turn on the aom/eom if we've been told a value.
				if args or kwargs:
					self.__intensity_channel.constant(t, *args, **kwargs)
				#else turn on to whatever was last set.
			self.is_on = True
		return 0

	def constant(self, t, *args, overload=False, **kwargs):
		#save args, and kwargs as they get modified after self.turnon(t) call for some reason
		_args = args
		_kwargs = kwargs
		self.turnon(t, overload=overload)
		self.__intensity_channel.constant(t, *_args, **_kwargs)

	def ramp(self, t, *args, overload=False, **kwargs):
		#save args, and kwargs as they get modified after self.turnon(t) call for some reason
		_args = args
		_kwargs = kwargs
		self.turnon(t, overload=overload)
		return self.__intensity_channel.ramp(t, *_args, **_kwargs)

class LaserBeam():
	""" 

	This is a template that holds functions for controlling the laser beam
	properties of a *single beampath*: intensity, and frequency. This class
	mostly just holds together, semantically, the two controllers for the
	intensity and frequency of our laserbeam.

	"""

	intensity	= None
	frequency	= None

	def __init__(self, intensity_control=None, frequency_control=None):
		'''
			Accepts arguments of the type `LaserIntensity`, and `LaserFrequency`.

			Each of the objects of these types define all the control methods for
			`self.intensity` and `self.frequency`.
			
			I want to particular about how my classes distinguish between the channel
			and the custom functions defined in the `LaserIntensity` and
			`LaserFrequency` classes.
		'''
		#save the controller
		self.intensity = intensity_control
		self.frequency = frequency_control
		super().__init__()

	def turnoff(self, *args, **kwargs):
		'''
			Calls the turn off method in the intensity controller.
		'''

		return self.intensity.turnoff(*args,**kwargs)

class Laser():
	'''
		This keeps track of the various laser beampaths that a single laser can be the source of. This is good for grouping our beampaths symantically.
		This is all it can do functionally.

		The really laser managment must be done in the LaserBeam class.

		E.g:

		```python
		green      	= Laser()
		green.probe	= LaserBeam()
		green.pump 	= LaserBeam() 
		```
	'''

#Specific Lasers:

class BlueLaser(Laser):

	#beampath names go here
	mot = None

	def __init__(self):
		''' 

		Defines the `LaserBeam`s, and `LaserIntensity` and `LaserFrequency`
		controls.

		Beampaths: (mot)
		'''

		#define the beampaths
		self.mot = LaserBeam(
				intensity_control	= LaserIntensity(
				                 		intensity_channel	= blue_mot_power,
				                 		shutter_channel  	= blue_mot_shutter
				                 	),
				frequency_control	= None
			)


class ProbeSidebandRFSwitch():
	def enable(self,t):
		probe_power_switch.enable(t)
		probe_sideband_power_switch.enable(t)
		probe_power_error_modulation.constant(t, value=0*mV)
		probe_sideband_cooling_rf_switch.enable(t)
	def disable(self,t ):
		probe_power_switch.disable(t)
		probe_sideband_power_switch.disable(t)
		probe_power_error_modulation.constant(t, value=2.95)
		# probe_power_error_modulation.constant(t, value=5)
		probe_sideband_cooling_rf_switch.disable(t)

class CoolingSigmaRFSwitch():
	def enable(self,t):
		probe_power_switch.enable(t)
		probe_sideband_cooling_rf_switch.disable(t)
		probe_power_error_modulation.constant(t, value=0*mV)
	def disable(self,t):
		probe_power_switch.disable(t)
		probe_power_error_modulation.constant(t, value=2.95)
		probe_sideband_cooling_rf_switch.enable(t)
class GreenLaser(Laser):

	#beampath names go here
	probe        	= None 
	pump         	= None #needs P7888 monitor
	mot          	= None
	cooling_pi   	= None
	cooling_sigma	= None

	def __init__(self):
		ms = 1e-3
		# a custom definition to combine two rf switches
		builtins.combined_probe_sideband_power_switch = ProbeSidebandRFSwitch()
		builtins.combined_probe_cooling_sigma_power_switch = CoolingSigmaRFSwitch()
		#define the beampaths
		self.mot = LaserBeam(
				intensity_control = LaserIntensity(
						intensity_channel = green_mot_power,
						rf_switch_channel = green_mot_power_switch,
						shutter_channel = green_mot_shutter,
						shutter_opentime = 4.9*ms,
						shutter_closetime = 6.2*ms
					),
				frequency_control = None,
			)

		self.pump = LaserBeam(
				intensity_control = LaserIntensity(
						intensity_channel = pump_power,
						shutter_channel = pump_power_switch,
						# shutter_closetime = 1*ms
					),
				frequency_control = None,
			)

		ms = 1e-3
		self.probe_shutter = probe_shutter
		self.cooling_shutter = cooling_sigma_shutter
		self.probe = LaserBeam(
				intensity_control = LaserIntensity(
						intensity_channel	= probe_sideband_power,
						rf_switch_channel	= combined_probe_sideband_power_switch,
						shutter_channel  	= probe_sideband_shutter,
						shutter_closetime	= 5.2*ms,
						shutter_opentime 	= 5.6*ms
					),
				frequency_control = probe_sideband_frequency,
			)

		self.cooling_sigma = LaserBeam(				
		        intensity_control = LaserIntensity(
						intensity_channel	= cooling_sigma_plus_power,
						rf_switch_channel	= combined_probe_cooling_sigma_power_switch,
						shutter_channel  	= cooling_sigma_shutter,
						shutter_closetime	= 6.28*ms,
						shutter_opentime 	= 3.36*ms
					),
				frequency_control = cooling_sideband_frequency,#SRS FM input
			)


		self.cooling_pi = LaserBeam(
				intensity_control = LaserIntensity(
						intensity_channel = cooling_pi_power,
						rf_switch_channel = cooling_pi_power_switch,
						shutter_channel = cooling_pi_shutter
					),
				frequency_control = None,
			)

class RedLaser(Laser):

	#beampath names go here
	cavity    	= None
	transverse	= None

	def __init__(self):
		self.cavity = LaserBeam(
				intensity_control = LaserIntensity(
						intensity_channel = red_cavity_power,
						rf_switch_channel = red_cavity_power_switch
					)
			)

		self.transverse = LaserBeam(
				intensity_control = LaserIntensity(
						intensity_channel = red_transverse_power
					)
			)



if __name__ == '__main__':
	pass
from labscript import start, stop
from labscriptlib.ybclock.connection_table import define_connection_table

def repeat_p7888_start_triggers(ti, tf, dt):
	'''
		Our data taking relies on sending multiple start pulses to time photons for long durations.

		It seems that to take reliable data in the configuration we have now, the start rate
		needs to be 1 kHz at least.
	'''
	t = ti
	while t < tf:
		p7888_start_trigger.enable(t)
		t += dt/2
		p7888_start_trigger.disable(t)
		t += dt/2

def send_fake_photons(ti,tf,dt):
	'''
		This is to emulate the flushing we'll need to do. It sends fake photon events to the card to
		fill up the buffer so it sends the whole batch of photon datas to the PC/file or whatever it is.

	'''
	t = ti
	while t < tf:
		p7888_flushing_channel.enable(t)
		t += dt/2
		p7888_flushing_channel.disable(t)
		t += dt/2


def send_photons():
	''' Turns on the green pumping light. '''
	#set green power
	green_pumping_light.enable(t=0.0001)
	pump_aom_power.constant(t=0.0001, value=10)
	#scan green frequency
	pass

def diagnostics():
	pass


if __name__ == '__main__':
	define_connection_table()
	# Begin issuing labscript primitives
	# start() elicits the commencement of the shot
	start()

	send_photons()

	repeat_p7888_start_triggers(
		ti = 5.1,
		tf = 10,
		dt = 0.001
	)

	send_fake_photons(
		ti = 5.1,
		tf = 10,
		dt = 0.0001
	)

	
	stop(11)

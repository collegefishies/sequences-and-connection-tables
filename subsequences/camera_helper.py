'''
Functions for triggering the cameras.
'''
def trigger_the_cameras(t0, duration, frame_period_ms):

	trigger_voltage = 8;

	t = t0

	while t < t0 + duration:
		wide_range_camera_trigger.constant(t, value=trigger_voltage)
		one_to_one_camera_trigger.constant(t, value=trigger_voltage)
		t += 0.001*frame_period_ms/2
		wide_range_camera_trigger.constant(t, value=0)
		one_to_one_camera_trigger.constant(t, value=0)
		t += 0.001*frame_period_ms/2
		

	return duration

print("Imported 'camera_helper'")
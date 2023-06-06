from labscript import start, stop
from labscriptlib.ybclock.connection_table import define_connection_table
if __name__ == '__main__':
	define_connection_table()
	# Begin issuing labscript primitives
	# start() elicits the commencement of the shot
	start()

	# # simple expose methods test: success!
	for x in range(1,4):
		wide_angle_cam.expose(t=x*0.1,	name = f'wide_test_pic_{x}',	trigger_duration=0.03)
		isometric_cam.expose(t=x*0.1, 	name=f'iso_test_pic_{x}',   	trigger_duration=0.03)
	
	# print(wide_angle_cam_trigger)
	# wide_angle_cam_trigger.go_high_analog(t=0.0001)
	# wide_angle_cam_trigger.go_low_analog(t=0.1)
	# wide_angle_cam_trigger.trigger(t=0.1, duration=0.1)

	stop(0.5)

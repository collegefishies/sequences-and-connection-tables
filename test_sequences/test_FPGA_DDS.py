from labscript import start, stop
from labscriptlib.ybclock.connection_table import define_connection_table
if __name__ == '__main__':
	define_connection_table()
	# Begin issuing labscript primitives
	# start() elicits the commencement of the shot
	start()
	us = 10**-6
	ms = 10**-3
	# set trigger time of FPGA_DDS9
	FPGA_DDS9.triggerSet(10*us)
	green_frequency_fpga_trigger.enable(10*us)
	# set initial value of the DDS

	FPGA_DDS9._constant(100*us, int('1111', 2), 'freq', 8, 'MHz', 'initial value')
	# FPGA_DDS9._constant(105*ms, int('1111', 2), 'phase', 0, 'Degrees', 'initial value')
	FPGA_DDS9._constant(150*us, int('1111', 2), 'ampl', 1, '1', 'initial value')

	FPGA_DDS9._constant(200*us, int('1111', 2), 'freq', 10, 'MHz', '1st value')

	# FPGA_DDS9._constant(210*us, int('1111', 2), 'ampl', 0.5, '1', 'initial value')

	FPGA_DDS9._ramp(220*us, 0.02, int('1111',2), 'freq', 10, 'MHz', 10000, 'Hz', 100, 'end ramp')



	FPGA_DDS9._constant(300*us, int('1111', 2), 'ampl', 1, '1', 'initial value')

	FPGA_DDS9._constant(200*ms, int('1111', 2), 'ampl', 1, '1', '2st value')



	# FPGA_DDS9._constant(100*ms, int('1111', 2), 'freq', 80, 'MHz', 'initial value')
	# FPGA_DDS9._constant(105*ms, int('1011', 2), 'phas', 15, 'Degrees', 'initial value')
	# FPGA_DDS9._constant(110*ms, int('1110', 2), 'phas', 0, 'Degrees', 'initial value')
	# FPGA_DDS9._constant(120*ms, int('1111', 2), 'ampl', 1, '1', 'initial value')
	# FPGA_DDS9._constant(140*ms, int('0001', 2), 'freq', 81, 'MHz', 'initial value')
	# FPGA_DDS9._constant(160*ms, int('0010', 2), 'freq', 82, 'MHz', 'initial value')
	# FPGA_DDS9._constant(170*ms, int('1100', 2), 'freq', 79, 'MHz', 'initial value')
	# FPGA_DDS9._constant(180*ms, int('1111', 2), 'freq', 80, 'MHz', 'initial value')
	# # set first _ramp of the DDS
	# FPGA_DDS9._ramp(0.5, 0.2, int('1111', 2), 'freq', 80, 'MHz', 1000,'Hz', 1000, '_Ramp 1Hz per 1000 us at 0.5s')
	# FPGA_DDS9._ramp(0.71, 0.05, int('1111', 2), 'amp', 1, '1', -0.01,'1', 1000, '_Ramp 1Hz per 1 us at 0.5s')
	# FPGA_DDS9._ramp(0.82, 0.1, int('1111', 2), 'freq', 80, 'MHz', -2000,'Hz', 1000, '_Ramp 2Hz per 1 us at 0.71s')
	# FPGA_DDS9._ramp(0.93, 0.1, int('0001', 2), 'phase', 0, 'Degrees', 10,'Degrees', 1000, '_Ramp 2Hz per 1 us at 0.71s')

	# FPGA_DDS9._constant(1.2, int('1111', 2), 'freq', 80, 'MHz', 'end value')

	# ramp(self, t, dt, channel, Func, Data, unit1, rampstep, unit2, ramprate, description = ''):
	# _constant(self, t, channel=0, Func= 'freq', Data = 0, unit = 'None', description = '')
	t = 0.5
	green_frequency_fpga_trigger.disable(t)
	stop(t+0.1)

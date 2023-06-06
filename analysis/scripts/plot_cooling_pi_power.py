from lyse import *
import matplotlib.pyplot as plt

if __name__ == '__main__':
	try:
		run = Run(path)
		trace = run.get_trace('green_cooling_pi_monitor')
		plt.plot(trace[0], trace[1])
		plt.title("green_cooling_pi_monitor")
		plt.ylabel('V')
		plt.xlabel('Time')
	except Exception as e:
		print(e)
		pass
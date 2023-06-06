'''
    Records the start time of the program to a log file to be read later for calculating the total analysis time spent in lyse.
'''
import time
import os
import json

#log directory
log_dir = r'C:\Users\YbClockReloaded\labscript-suite\userlib\labscriptlib\ybclock\logs'

def main():
    #open the logfile
    log_file_name = os.path.join(log_dir, 'lyse-runtimes.json')
    with open(log_file_name, 'r') as f:
        #read the file and convert to a list
        data = json.load(f)

    #get all the durations from the list
    durations = []
    for element in data:
        if len(element) == 3:
            duration = element[2]
            durations.append(duration)

    #plot a histogram
    import matplotlib.pyplot as plt
    plt.hist(durations, bins=100)
    #make labels
    plt.xlabel('Duration (s)')
    plt.ylabel('Count')
    plt.title('Lyse Runtime Histogram')

if __name__ == '__main__':
    try:
        main()
    except:
        pass
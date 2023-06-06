'''
    
    PyQt Application for reading runtimes from the labscript log files then
    plotting them as histograms.

'''

from PyQt5 import QtWidgets, QtCore, QtGui
import matplotlib.pyplot as plt
from datetime import datetime
def main():
    #test the app model
    app = AppModel()
    app.get_runmanager_runtimes()
    app.get_BLACS_runtimes()

class AppModel():
    def __init__(self):
        pass

    def parse_log_lines(self, log_lines):
        #parse each line into date, debug, program, and comment
        split_log_lines = []
        for line in log_lines:
            try:
                #split the line into date, debug, program, and comment
                #split across the first three spaces
                split_line = line.split(' ', 3)
                date = split_line[0]
                time = split_line[1]
                debug = split_line[2]
                the_rest = split_line[3]
                #split the_rest into program and comment
                program = the_rest.split(': ', 1)[0]
                comment = the_rest.split(': ', 1)[1]
                #add the parsed line to the list as a dict
                split_log_lines.append({'date': date, 'time': time, 'debug': debug, 'program': program, 'comment': comment})
            except:
                pass
        return split_log_lines

    def get_runmanager_runtimes(self):
        runmanager_file_location = r"C:\Users\YbClockReloaded\labscript-suite\logs\runmanager.log"

        #read the entire file contents into a string
        with open(runmanager_file_location, 'r') as f:
            runmanager_file_contents = f.read()
        
        #split the string into a list of lines
        runmanager_file_lines = runmanager_file_contents.split('\n')

        #parse each line into date, debug, program, and comment
        parsed_log_lines = self.parse_log_lines(runmanager_file_lines)

        #find the lines that contain the word "Engage" in the "comment" field
        engage_lines = []
        for line in parsed_log_lines:
            if 'Engage' in line['comment']:
                engage_lines.append(line['time'])
        #find the lines that contain the word "end engage" in the "comment" field
        end_engage_lines = []
        for line in parsed_log_lines:
            if 'end engage' in line['comment']:
                end_engage_lines.append(line['time'])

        #make the lists equal length
        x = len(engage_lines)
        y = len(end_engage_lines)
        the_min = min(x, y)
        engage_lines = engage_lines[:the_min]
        end_engage_lines = end_engage_lines[:the_min]
        
        #convert the times to datetime objects
        engage_times = []
        end_engage_times = []
        for line in engage_lines:
            engage_times.append(datetime.strptime(line, '%H:%M:%S,%f'))
        for line in end_engage_lines:
            end_engage_times.append(datetime.strptime(line, '%H:%M:%S,%f'))
        
        #calculate the runtimes
        runtimes = []
        for i in range(len(engage_times)):
            runtimes.append(end_engage_times[i] - engage_times[i])
        #convert the runtimes to seconds
        runtimes_seconds = []
        for runtime in runtimes:
            runtimes_seconds.append(runtime.total_seconds())
        #plot the runtimes as a histogram
        print(runtimes_seconds)
        plt.hist(runtimes_seconds, bins=100)
        #label
        plt.xlabel('Runtime (seconds)')
        plt.ylabel('Number of Occurrences')
        plt.title('Runtimes for Runmanager')
        plt.show()

    def get_BLACS_runtimes(self):
        blacs_file_location = r"C:\Users\YbClockReloaded\labscript-suite\logs\BLACS.log"

        #read the entire file contents into a string
        with open(blacs_file_location, 'r') as f:
            blacs_file_contents = f.read()
        
        #split the string into a list of lines
        blacs_file_lines = blacs_file_contents.split('\n')

        #parse each line into date, debug, program, and comment
        parsed_log_lines = self.parse_log_lines(blacs_file_lines)

        #find the lines that contain the word "Request handler: Experiment added successfully " in the "comment" field
        engage_lines = []
        for line in parsed_log_lines:
            if 'Request handler: Experiment added successfully ' in line['comment']:
                engage_lines.append(line['time'])
        #find the lines that contain the word "All devices are back in static mode." in the "comment" field
        end_engage_lines = []
        for line in parsed_log_lines:
            if 'All devices are back in static mode.' in line['comment']:
                end_engage_lines.append(line['time'])

        #make the lists equal length
        if len(end_engage_lines) > len(engage_lines):
            #remove from the beginning of the lists until they are equal length
            engage_lines = engage_lines[len(end_engage_lines)-len(engage_lines):]
        elif len(end_engage_lines) < len(engage_lines):
            print("I don't know how this is possible but it is happening")    
        
        #convert the times to datetime objects
        engage_times = []
        end_engage_times = []
        for line in engage_lines:
            engage_times.append(datetime.strptime(line, '%H:%M:%S,%f'))
        for line in end_engage_lines:
            end_engage_times.append(datetime.strptime(line, '%H:%M:%S,%f'))
        
        #calculate the runtimes
        runtimes = []
        for i in range(len(engage_times)):
            runtimes.append(end_engage_times[i] - engage_times[i])
        #convert the runtimes to seconds
        runtimes_seconds = []
        for runtime in runtimes:
            runtimes_seconds.append(runtime.total_seconds())
        #plot the runtimes as a histogram
        print(runtimes_seconds)
        plt.hist(runtimes_seconds, bins=100)
        #label
        plt.xlabel('Runtime (seconds)')
        plt.ylabel('Number of Occurrences')
        plt.title('Runtimes for BLACS')
        plt.show()

        

        

        


class AppView(AppModel):
    pass
class AppController(AppView):
    pass

if __name__ == "__main__":
    main()
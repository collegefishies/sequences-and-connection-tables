'''
    Records the start time of the program to a log file to be read later for calculating the total analysis time spent in lyse.
'''
import time
import os
import json

#log directory
log_dir = r'C:\Users\YbClockReloaded\labscript-suite\userlib\labscriptlib\ybclock\logs'

def main():

    #get the current time in unix time
    end_time = time.time()

    #make the log file name
    log_file_name = os.path.join(log_dir, 'lyse-runtimes.json')
    
    #store the time as a two element tuple in a json file as readwrite
    with open(log_file_name, 'r+') as f:
        #read the file and convert to a list
        data = json.load(f)

        #get the last element from the list
        last_time = data[-1]

        #add the new time to the list
        last_time.append(end_time)
        #calculate the elapsed time
        elapsed_time = last_time[1] - last_time[0]
        #add the elapsed time to the list
        last_time.append(elapsed_time)

        #replace the last element with the new one
        data[-1] = last_time
        
        #clear the file
        f.seek(0)
        f.truncate()

        #write the list back to the file
        #with new lines and tabs to make it readable
        json.dump(data, f, indent=4)

def delete_the_log_file(log_file_name=r'C:\Users\YbClockReloaded\labscript-suite\userlib\labscriptlib\ybclock\logs\lyse-runtimes.json'):
    #delete the log file
    if os.path.exists(log_file_name):
        log_file_name = os.path.join(log_dir, 'lyse-runtimes.json')
        os.remove(log_file_name)
def create_the_log_file_if_not_exists(log_file_name=r'C:\Users\YbClockReloaded\labscript-suite\userlib\labscriptlib\ybclock\logs\lyse-runtimes.json'):
    #create the log file if it doesn't exist
    if not os.path.exists(log_file_name):
        with open(log_file_name, 'w') as f:
            json.dump([], f)
if __name__ == '__main__':
    try:
        main()
    except:
        pass
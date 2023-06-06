import runmanager.remote as rm
import time


def read_queue():
    # read a number from a file written to a hard drive
    try:
        with open('queue.txt', 'r') as f:
            queue_number = f.read()
        return int(queue_number)
    except:
        return 0

def write_queue(queue_number):
    # write a number to a file on the hard drive
    with open('queue.txt', 'w') as f:
        f.write(str(queue_number))
    return True

def main():
    #run as many shots as there are in the queue
    queue_number = read_queue()
    for i in range(queue_number):
        rm.engage()
    #set the queue number to 0
    write_queue(0)
    return queue_number

if __name__ == '__main__':
    #time main() and print the time it took
    start_time = time.time()
    queue_number = main()
    print('Time: ' + str(time.time() - start_time))
    #print time per queue
    print('Time per queue: ' + str((time.time() - start_time)/(queue_number)))
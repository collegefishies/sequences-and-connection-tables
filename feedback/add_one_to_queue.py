from labscriptlib.ybclock.feedback.engage_next_shot import write_queue, read_queue


def main():
    queue_number = read_queue()
    queue_number = int(queue_number) + 1
    queue_number = str(queue_number)
    write_queue(queue_number)
    print('Queue number: ' + queue_number)
    return queue_number


if __name__ == '__main__':
    main()

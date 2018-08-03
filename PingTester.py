#####################################
## v2.0                            ##
## can return # of dropped packets ##
#####################################

import sys
import os
import platform
import subprocess
import Queue
import threading
import socket       # For DNS lookup

def worker_func(ping_args, pending, done):
    try:
        while True:
            # Get the next address to ping.
            address = pending.get_nowait()

            ping = subprocess.Popen(ping_args + [address],
                stdout = subprocess.PIPE,
                stderr = subprocess.PIPE
            )
            out, error = ping.communicate()

            # Output the result to the 'done' queue.
            done.put((out, error))
    except Queue.Empty:
        # No more addresses.
        pass
    finally:
        # Tell the main thread that a worker is about to terminate.
        done.put(None)
        
def stripPercentLost(data_string):
	# This has only been tested on Linux
	percent_sign_index = data_string.find('%')
	percent_begin_index = percent_sign_index
	while True:
		if data_string[percent_begin_index] == ' ': 
			percent_begin_index += 1
			break
		percent_begin_index -= 1
	return float(data_string[percent_begin_index:percent_sign_index])

def stripHostIP(data_string):
	host_ip = data_string.split(' ')[1]
	return host_ip

def startPingTests(host_ip_list = [], return_packets_count = False):
    # The number of workers.
    NUM_WORKERS = 4

    plat = platform.system()


    # The arguments for the ping, excluding the address
    if plat == "Windows":
        ping_args = ["ping", "-n", "1", "-l", "1", "-w", "100"]
    elif plat == "Linux":
        ping_args = ["ping", "-c", "1", "-l", "1", "-s", "1", "-W", "1"]
    else:
        raise ValueError("Unknown platform")

    # The queue of addresses to ping
    pending = Queue.Queue()

    # The queue of results
    done = Queue.Queue()

    # Create all the workers
    workers = []
    for _ in range(NUM_WORKERS):
        workers.append(threading.Thread(target=worker_func, args=(ping_args, pending, done)))

	# If host ip's were not passed in, load them from hosts.txt
	if not host_ip_list:
		# Put all the addresses into the 'pending' queue.
		scriptDir = sys.path[0]
		hosts = os.path.join(scriptDir, 'hosts.txt')
    
		with open(hosts, "r") as hostsFile:
			for line in hostsFile:

				line = line.strip() # Strip newline

				# Check if line is ip address, if not, perform dns lookup
				for char in line:
					if char.isalpha():
						print 'Performing DNS lookup on', line
						line = socket.gethostbyname(line)
						print 'Returned DNS:', line
						break

				pending.put(line.strip())
	else:
		# IP list was passed in then queue those
		for raw_line in host_ip_list:
			pending.put(raw_line.strip())

    # Start all the workers.
    for w in workers:
        w.daemon = True
        w.start()

    # Print out the results as they arrive.
    numTerminated = 0
    # Set up dictionary to hold ping results
    results_dict = {}
    # Keep track of dropped packets
    packets_lost = 0
    packets_total = 0
    while numTerminated < NUM_WORKERS:
        result = done.get()
        if result is None:
            # A worker is about to terminate.
            numTerminated += 1
        else:
			percent_lost = stripPercentLost(result[0])
			# Convert % lost to int
			packets_lost  += percent_lost * NUM_WORKERS
			packets_total += NUM_WORKERS
			
			# Set fail limit of % packets lost (>= fails)
			percent_lost_fail_limit = 100
			
			# Return pass or fail for that worker_func
			if percent_lost >= percent_lost_fail_limit:
				results_dict[stripHostIP(result[0])] = 0
			else:
				results_dict[stripHostIP(result[0])] = 1

    # Wait for all the workers to finish
    for w in workers:
        w.join()

	# Return pass/fail and packets info
	if return_packets_count:
		return results_dict, packets_lost, packets_total
	else:
		return results_dict
	
def ping(ip_address, quiet = True):
	result = startPingTests([ip_address])
	if result[ip_address] == 1:
		if not quiet: print 'PING PASSED {}'.format(ip_address)
		return 1
	else:
		if not quiet: print 'PING FAILED {}'.format(ip_address)
		return 0

if __name__ == '__main__':
    print startPingTests(host_ip_list = ['8.8.8.8'])

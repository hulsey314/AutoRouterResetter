## Monitors internet connection to make sure it stays up. Checks if
## network is up when the internet fails.  Attempts to reset one or both
## of them using a relay on the GPIO


from pingTester import ping
import LEDControl as LED
import RPi.GPIO as GPIO
from datetime import datetime
import csv
from time import sleep, time

def logEvent(event, info_1 = '', info_2 = ''):
	# Get full time stamp
	full_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
	# Trim 6 digits of ms down to 3
	ts = full_ts[:-3]

	log_line = [ts, event, info_1, info_2]
	print 'Logging event:', log_line
	with open(log_path, 'a') as f:
		writer = csv.writer(f)
		writer.writerow(log_line)
		
def checkRouter(quiet = True):
	router_ping_passed = ping(ROUTER_IP_ADDRESS)
	if router_ping_passed:
		if not quiet: print 'Router ping passed.'
		return 1
	else:
		if not quiet: print 'Router ping failed.'
		return 0

def checkInternet(quiet = True):
	internet_ping_passed = ping(GOOGLE_IP_ADDRESS)
	if internet_ping_passed:
		if not quiet: print 'Internet ping passed'
		return 1
	else:
		if not quiet: print 'Internet ping failed'
		return 0

def turnOffRouter():
	print 'Turning router OFF'
	logEvent('Router turning off')
	GPIO.output(router_relay_pin, GPIO.LOW)
	
def turnOnRouter():
	print 'Turning router ON'
	logEvent('Router turning on')
	GPIO.output(router_relay_pin, GPIO.HIGH)
	
def turnOffModem():
	print 'Turning modem OFF'
	logEvent('Modem turning off')
	GPIO.output(modem_relay_pin, GPIO.LOW)
	
def turnOnModem():
	print 'Turning modem ON'
	logEvent('Modem turning on')
	GPIO.output(modem_relay_pin, GPIO.HIGH)

def resetRouter():
	# Turn off router
	turnOffRouter()
	# Wait 3 seconds before turning router back on
	sleep(3)
	# Turn on router
	turnOnRouter()
	
def resetModem(additional_modem_delay_time = 0):
	print 'Modem and router restarting...'
	# Turn off router
	turnOffRouter()
	# Turn off modem
	turnOffModem()
	# Wait 3 seconds before turning modem back on
	sleep(3)
	# Turn on modem
	turnOnModem()


# Set log path
log_path = 'network_log.csv'

# Log monitor initialization
logEvent('Monitor loading...')

#~ # Router/modem relay pins
router_relay_pin	= 17
modem_relay_pin 	= 27

# Reset router and modem button pin number
reset_button_pin 	= 25

# LEDs
green_led_pin 		= 9
yellow_1_led_pin 	= 10
yellow_2_led_pin 	= 11
red_led_pin 		= 24

### GPIO SETUP ###

# Set mode
GPIO.setmode(GPIO.BCM)

# Turn off any GPIO warnings
GPIO.setwarnings(False)

# Setup relays to reset router and modem
GPIO.setup(router_relay_pin, GPIO.OUT)
GPIO.setup(modem_relay_pin,  GPIO.OUT)

# Setup button for manual reset
GPIO.setup(reset_button_pin, GPIO.IN, pull_up_down = GPIO.PUD_UP)

# Set test addresses to ping
GOOGLE_IP_ADDRESS = '8.8.8.8'
ROUTER_IP_ADDRESS = '192.168.0.1'

# Set limits for checks
network_ping_frequency   = 5	# Network ping test frequency in s

internet_ping_retry_delay = 3	# Internet ping retry delay on fail
internet_ping_retry_limit = 3	# Internet ping retry limit
internet_ping_retry_count = 0	# Count of internet ping retries
internet_ping_time = time()		# Time used when retry limit is hit
internet_fail_wait_time = 300	# Time to wait before retrying internet

router_ping_retry_delay = 2 	# Router ping retry delay on fail
router_ping_retry_limit = 10	# Router ping retry limit
router_ping_retry_count = 0		# Count of router ping retries
router_ping_time = time() 		# Time used when retry limit is hit
router_restart_count = 0 		# Count of router restart attempts
router_restart_limit = 10		# Router restart attempt limit

button_check_frequency = .5		# How often to check reset button

last_button_check	= time()	# Get current time
last_network_check	= time()	# Get current time

router_reset_delay = 120		# Time to wait for router to reconnect
modem_reset_delay  = 120		# Time to wait for modem to reconnect


print """
 /=========================\\
| Automatic Router Resetter |
|           v 0.1           |
 \\========================/

 ----------------------
 Router Monitor started
 ----------------------
"""

# Log monitor load successful
logEvent('Monitor starting...')
LED.changeState('checking')
internet_working = checkInternet()

# Set ping times
internet_ping_time = time()
network_ping_time = time()

if internet_working:
	logEvent('Internet: Working')
	LED.changeState('good')
else:
	router_working = checkRouter()
	if router_working:
		logEvent('Internet: DOWN, Router: Working')
		LED.changeState('modem_error')
	else:
		logEvent('Internet: DOWN, Router: DOWN')
		LED.changeState('both_error')

			
# Sleep delay to use less CPU. Min reaction time to button presses
check_loop_delay = .1


# Begin loop to watch for button presses and check internet
while True:
	# Allow reset button to force reset
	force_reset = False
	# Check if manual reset buttons are pressed
	if time()-last_button_check >= button_check_frequency:
		# Set last_button_check to current time
		last_button_check = time()
			
		if GPIO.input(reset_button_pin) == 0:
			print 'Reset button pressed!'
			logEvent('Reset button pressed')
			
			# Watch how long button is held down
			long_hold = 3
			button_press_time = time()
			# Delay some ms between checks (in s)
			button_hold_check_delay = .05
			while GPIO.input(reset_button_pin) == 0:
				sleep(button_hold_check_delay)
			button_hold_time = time() - button_press_time
			# Recheck internet and modem on short press
			if button_hold_time < long_hold:
				# Set last_network_check to 0 to force recheck
				last_network_check = 0
				logEvent('Forcing network recheck', button_hold_time)
			else:
				# Long press, reset network
				force_reset = True
				logEvent('Forcing router/modem reset', button_hold_time)
			
			
			
	# Check router every internet_ping_frequency seconds
	if time()-last_network_check >= network_ping_frequency:	
		LED.changeState('checking')
		router_working = checkRouter()
		last_network_check = time()
	
		if router_working:
			LED.changeState('good')		
		else:
			LED.changeState('router_error')
						
			##################
			# Router restart #
			##################	
			
			# Test router ping again
			router_ping_retry_count = 0
			while router_ping_retry_count < router_ping_retry_limit:
				router_ping_retry_count += 1
				logEvent('Router ping failed!', 'Retrying ping. (Attempt: {}/{})'.format(router_ping_retry_count,router_ping_retry_limit))
				LED.changeState('router_error_checking')
				router_working = checkRouter()
				
				if router_working:
					LED.changeState('good')
					break
					
				sleep(router_ping_retry_delay)
				
			if router_working:
				# Log event
				logEvent('Router ping retry passed')
			else:
				if router_restart_count >= router_restart_limit:
					# Log event
					logEvent('Router ping failed!', 'Restart limit reached! No action taken. (Attempts: {})'.format(router_restart_count))
					LED.changeState('router_error')
				else:
					router_restart_count += 1
					# Log event
					logEvent('Router ping failed!', 'Restarting router. (Attempt: {})'.format(router_restart_count))
					# Restart router
					LED.changeState('restarting')
					resetRouter()
				 
					# Start checking if reset was successful
					time_limit = 90 # Time till reset was unsuccessful
					reset_time = time()
					reset_check_frequency = .5 # How often to ping router
					while time() - reset_time < time_limit:
						LED.changeState('checking')
						router_working = checkRouter()
						router_ping_time = time()
						if router_working: break
						sleep(reset_check_frequency)
						
					if router_working:
						reset_time_elapsed = round(time()-reset_time, 2)
						LED.changeState('good')
						logEvent('Router reset was successful ({}s)'.format(reset_time_elapsed))
						router_ping_retry_count = 0
					else:
						LED.changeState('router_error')
						logEvent('Router reset was not successful after {}s'.format(time_limit))
			
	# Sleep briefly to save CPU
	sleep(check_loop_delay)


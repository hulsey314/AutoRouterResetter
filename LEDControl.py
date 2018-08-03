import RPi.GPIO as GPIO
from time import sleep, time

def ledChange(LED, new_state):
	if new_state in [0, '0', 'off']: new_state = GPIO.LOW
	if new_state in[1, '1', 'on']: 	 new_state = GPIO.HIGH

	if LED in ['green','g']: 	   	LED = green_led_pin
	elif LED in ['yellow1', 'y1']: 	LED = yellow_1_led_pin
	elif LED in ['yellow2', 'y2']: 	LED = yellow_2_led_pin
	elif LED in ['red', 'r']: 		LED = red_led_pin
	
	GPIO.output(LED, new_state)

def ledOn(LED):
	ledChange(LED, 1)

def ledOff(LED):
	ledChange(LED, 0)

def allOn():
	led_colors = ['g', 'y1', 'y2', 'r']
	for led_color in led_colors:
		ledChange(led_color, 1)

def allOff():
	led_colors = ['g', 'y1', 'y2', 'r']
	for led_color in led_colors:
		ledChange(led_color, 0)
		
def runUp(turn_on_or_off = 'on', delay = .2, start_delay = -1):
	led_colors = ['g', 'y1', 'y2', 'r']
	
	if turn_on_or_off == 'on':
		allOff()
		new_state = 1
	else:
		allOn()
		new_state = 0
	if start_delay == -1:
		start_delay = delay
	sleep(start_delay)
	for color_index in xrange(4):
		ledChange(led_colors[color_index], new_state)
		sleep(delay)

		
def runDown(delay = .2):
	led_colors = ['g', 'y1', 'y2', 'r']
	
	allOff()
	sleep(delay)
	for color_index in xrange(3, -1, -1):
		ledChange(led_colors[color_index], 1)
		sleep(delay)

def changeState(led_state = 'good'):
	# States:
	# good = Green on, others off
	# checking = Green on, yellow1 on, others off
	# error = Red on, others off
	# router_error = Red on, yellow1 on, others off
	# modem_error = Red on, yellow2 on, others off
	# both_error = Red on, yellow1 on, yellow2 on, green off
	
	led_state = led_state.lower()
	
	if led_state ==  'good':
		led_pattern = [1,0,0,0]
	elif led_state =='checking':
		led_pattern = [1,1,0,0]
	elif led_state =='error':
		led_pattern = [0,0,0,1]
	elif led_state =='router_error_checking':
		led_pattern = [0,1,0,1]
	elif led_state =='router_error':
		led_pattern = [0,1,0,1]
	elif led_state =='modem_error':
		led_pattern = [0,0,1,1]
	elif led_state =='both_error':
		led_pattern = [0,1,1,1]
	elif led_state =='restarting':
		led_pattern = [1,1,1,1]
	else:
		print 'ERROR: LED state not recognized! Turning all LEDs on'
		led_pattern = [1,1,1,1]
	
	ledChange('g',  led_pattern[0])
	ledChange('y1', led_pattern[1])
	ledChange('y2', led_pattern[2])
	ledChange('r',  led_pattern[3])
	
	
########################################################################

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

# Setup LEDs
GPIO.setup(green_led_pin, GPIO.OUT)
GPIO.setup(yellow_1_led_pin,  GPIO.OUT)
GPIO.setup(yellow_2_led_pin,  GPIO.OUT)
GPIO.setup(red_led_pin,  GPIO.OUT)


# Setup button for manual reset
GPIO.setup(reset_button_pin, GPIO.IN, pull_up_down = GPIO.PUD_UP)

allOff()
r_state = False
y1_state = False
y2_state = False
g_state = False

last_command = 'g'

if __name__ == '__main__':
	#### DEMO ####
	print 'Demo Mode - Double press button to cycle light patterns'
	
	button_down = False
	double_press_speed = .5
	last_released = time()

	print 'Watching button...'
	demo = 0
	demos = 3
	while True:
		if GPIO.input(reset_button_pin):
			if button_down == True:
				# Button was released
				button_down = False
				if not demo:
					if time() - last_released < double_press_speed:
						# Button was double pressed
						print 'Demo mode on'
						demo = 1
					else:
						last_released = time()	
		else:
			# Ignore button if already down
			if not button_down:
				button_down = True
				if demo:
					demo += 1
					if demo > demos:
						print 'Demo mode off'
						demo = 0
					else:
						print 'Demo changed:', demo
					sleep(.5)

		if demo == 0:
			# No demo, just turn lights on or off
			if button_down:
				allOn()
			else:
				allOff()
			
			sleep(.05)
		
		elif demo == 1:

			run_speed = .15
			runUp('on',run_speed)
			runUp('off',run_speed, 0)

		elif demo == 2:

			run_speed = .1
			runUp('on',run_speed)
			runUp('off',run_speed, 0)		

		elif demo == 3:

			run_speed = .05
			runUp('on',run_speed)
			runUp('off',run_speed, 0)	
		



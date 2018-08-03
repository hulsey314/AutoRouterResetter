from email.MIMEMultipart import MIMEMultipart
from email.MIMEImage import MIMEImage
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import Encoders

import smtplib
import os
from time import strftime, localtime, 

def sendAttachment(receiver, files = [], subject = ''):
	# Check for email settings file and create if missing
	EMAIL_SETTINGS_FILE = 'EmailSettings.ben'
	if not os.path.isfile(EMAIL_SETTINGS_FILE):
		print 'Email settings not found!'
		print 'Please enter your GMail address and password'
		
		while True:
			MY_EMAIL_ADDRESS = raw_input('Email address: ').lower()
			if not MY_EMAIL_ADDRESS.endswith('@gmail.com'):
				print 'Please enter a valid GMail address'
			else:
				break
				
		while True:
			MY_PASSWORD = raw_input('Email password: ')
			if not MY_PASSWORD:
				print 'Password cannot be blank. Please try again.'
			else:
				break
		# Save settings to file		
		with open(EMAIL_SETTINGS_FILE, 'w') as f:
			f.writelines([MY_EMAIL_ADDRESS + '\n', MY_PASSWORD])
		print 'Email settings file created.'
		
	else:
		# Email settings file found, load address and password
		with open(EMAIL_SETTINGS_FILE, 'r') as f:
			MY_EMAIL_ADDRESS = f.readline().strip('\n')
			MY_PASSWORD = f.readline()
		print 'Email settings loaded'
		print 'Email address:', MY_EMAIL_ADDRESS
		print MY_PASSWORD
			
	SMTP_SERVER = 'smtp.gmail.com'
	SMTP_PORT = 587

	msg = MIMEMultipart()
	msg['Subject'] = subject
	msg['To'] = receiver
	msg['From'] = MY_EMAIL_ADDRESS

	for f in files:
		print 'Attaching:', f
		part = MIMEBase('application', "octet-stream")
		part.set_payload(open(f, "rb").read())
		Encoders.encode_base64(part)
		part.add_header('Content-Disposition', 'attachment; filename="{0}"'.format(os.path.basename(f)))
		msg.attach(part)

	print 'Logging into email'
	server = smtplib.SMTP(SMTP_SERVER,SMTP_PORT)
	server.ehlo()
	server.starttls()
	server.ehlo
	server.login(MY_EMAIL_ADDRESS,MY_PASSWORD)
	print 'Sending...'
	server.sendmail(MY_EMAIL_ADDRESS, receiver, msg.as_string())
	server.quit()
	print 'Sent!'
	

sendAttachment('hulsey314@gmail.com')

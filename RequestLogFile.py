from simpleMMS import sendAttachment
from CSVtoXLSX import convertCSVtoXLSX
import sys


if __name__ == '__main__':
	if len(sys.argv) == 1:
		print 'Please enter the address or your name as argument'
	else:
		convertCSVtoXLSX('network_log.csv')
		sendAttachment(sys.argv[1], ['network_log.xlsx'])

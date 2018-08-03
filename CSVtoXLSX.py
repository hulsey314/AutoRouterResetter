# Converts log file csv to xlsx

import csv
import xlsxwriter
import sys
import simpleMMS

def convertCSVtoXLSX(file_name):
	# Converts log file csv to xlsx
	if file_name.endswith('.csv'):
		file_name = file_name[:-4]
	excel_filename = file_name + '.xlsx'
	excelFile = xlsxwriter.Workbook(excel_filename)
	worksheet = excelFile.add_worksheet()
	with open(file_name + '.csv', 'rb')  as f:
		content = csv.reader(f)
		for index_row, data_in_row in enumerate(content):
			for index_col, data_in_cell in enumerate(data_in_row):
				worksheet.write(index_row, index_col, data_in_cell)
				
	excelFile.close()
	
	return excel_filename

CSV_filename = 'network_log.csv'	
print 'Converting {} to xlsx file...'.format(CSV_filename)
excel_filename = convertCSVtoXLSX(CSV_filename)


if __name__ == '__main__':
	if len(sys.argv) == 2:
		# Send attachment to email address
		to_email_address = sys.argv[1]
		print 'Sending xlsx file to {}'.format(to_email_address)
		simpleMMS.sendAttachment(to_email_address, [excel_filename], 'XLSX File: {}'.format(excel_filename))
		

print 'CSV successfully converted to file {}'.format(excel_filename)

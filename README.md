# AutoRouterResetter
For use on a Raspberry Pi.  This program monitors internet connectivity and resets the router using a relay as needed.  It logs events to file which can be converted to Excel XLSX format and emailed.  The current program and router status is shown using 4 LEDs, and a button can be pressed to manually recheck connectivity or reset the router.

Usage:
- Run AutoRouterResetter.py when Raspberry Pi is turned on to begin monitoring internet and reset button presses
- Run RequestLogFile.py [email address] to convert log file to XLSX and email to given address

Dependencies:
- XLSX Writer https://xlsxwriter.readthedocs.io/

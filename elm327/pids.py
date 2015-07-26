"""
Python module presenting an API to an ELM327 serial interface
(C) 2015 Jamie Fraser <fwaggle@fwaggle.org>
http://github.com/fwaggle/pyELM327

Please see License.txt and Readme.md.
"""

__pids ={
		0x01: {
			0x0C: {
				'Name': 'Engine RPM',
				'Units': 'RPM',
				'Pattern': '^[A-Z0-9]{2} [A-Z0-9]{2} ([A-Z0-9]{2}) ([A-Z0-9]{2}) $',
				'Value': lambda m: ((int(m.group(1),16) * 256) + int(m.group(2), 16))/4},
			},
		}
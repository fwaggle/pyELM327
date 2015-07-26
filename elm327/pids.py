"""
Python module presenting an API to an ELM327 serial interface
(C) 2015 Jamie Fraser <fwaggle@fwaggle.org>
http://github.com/fwaggle/pyELM327

Please see License.txt and Readme.md.
"""

# Pretty much taken from https://en.wikipedia.org/wiki/OBD-II_PIDs
__pids ={
		0x01: {
			0x04: {
				'Name': 'Calculated engine load value',
				'Units': '%',
				'Pattern': '^[A-Z0-9]{2} [A-Z0-9]{2} ([A-Z0-9]{2}) $',
				'Value': lambda m: int(m.group(1),16) * 100 / 255 },
			0x05: {
				'Name': 'Engine coolant temperature',
				'Units': '*C',
				'Pattern': '^[A-Z0-9]{2} [A-Z0-9]{2} ([A-Z0-9]{2}) $',
				'Value': lambda m: int(m.group(1),16) - 40 },
			0x06: {
				'Name': 'Short term fuel % trim - Bank 1',
				'Units': '%',
				'Pattern': '^[A-Z0-9]{2} [A-Z0-9]{2} ([A-Z0-9]{2}) $',
				'Value': lambda m: (int(m.group(1),16)-128) * 100 / 128 },
			0x07: {
				'Name': 'Long term fuel % trim - Bank 1',
				'Units': '%',
				'Pattern': '^[A-Z0-9]{2} [A-Z0-9]{2} ([A-Z0-9]{2}) $',
				'Value': lambda m: (int(m.group(1),16)-128) * 100 / 128 },
			0x08: {
				'Name': 'Short term fuel % trim - Bank 2',
				'Units': '%',
				'Pattern': '^[A-Z0-9]{2} [A-Z0-9]{2} ([A-Z0-9]{2}) $',
				'Value': lambda m: (int(m.group(1),16)-128) * 100 / 128 },
			0x09: {
				'Name': 'Long term fuel % trim - Bank 2',
				'Units': '%',
				'Pattern': '^[A-Z0-9]{2} [A-Z0-9]{2} ([A-Z0-9]{2}) $',
				'Value': lambda m: (int(m.group(1),16)-128) * 100 / 128 },
			0x0A: {
				'Name': 'Fuel pressure',
				'Units': 'kPa (gauge)',
				'Pattern': '^[A-Z0-9]{2} [A-Z0-9]{2} ([A-Z0-9]{2}) $',
				'Value': lambda m: int(m.group(1),16) * 3 },
			0x0B: {
				'Name': 'Intake manifold absolute pressure',
				'Units': 'kPa (absolute)',
				'Pattern': '^[A-Z0-9]{2} [A-Z0-9]{2} ([A-Z0-9]{2}) $',
				'Value': lambda m: int(m.group(1),16) },
			0x0C: {
				'Name': 'Engine RPM',
				'Units': 'RPM',
				'Pattern': '^[A-Z0-9]{2} [A-Z0-9]{2} ([A-Z0-9]{2}) ([A-Z0-9]{2}) $',
				'Value': lambda m: ((int(m.group(1),16) * 256) + int(m.group(2), 16))/4},
			},
			0x0D: {
				'Name': 'Vehicle speed',
				'Units': 'km/h',
				'Pattern': '^[A-Z0-9]{2} [A-Z0-9]{2} ([A-Z0-9]{2}) $',
				'Value': lambda m: int(m.group(1),16) },
			0x0E: {
				'Name': 'Timing advance',
				'Units': '* rel #1 cylinder',
				'Pattern': '^[A-Z0-9]{2} [A-Z0-9]{2} ([A-Z0-9]{2}) $',
				'Value': lambda m: (int(m.group(1),16) - 128) / 2 },
			0x0F: {
				'Name': 'Intake air temperature',
				'Units': '*C',
				'Pattern': '^[A-Z0-9]{2} [A-Z0-9]{2} ([A-Z0-9]{2}) $',
				'Value': lambda m: int(m.group(1),16) - 40 },
		}
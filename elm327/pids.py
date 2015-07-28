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
				'Value': lambda m: int(m.group(1),16) * 100.0 / 255 },
			0x05: {
				'Name': 'Engine coolant temperature',
				'Units': '*C',
				'Pattern': '^[A-Z0-9]{2} [A-Z0-9]{2} ([A-Z0-9]{2}) $',
				'Value': lambda m: int(m.group(1),16) - 40 },
			0x06: {
				'Name': 'Short term fuel % trim - Bank 1',
				'Units': '%',
				'Pattern': '^[A-Z0-9]{2} [A-Z0-9]{2} ([A-Z0-9]{2}) $',
				'Value': lambda m: (int(m.group(1),16)-128) * 100.0 / 128 },
			0x07: {
				'Name': 'Long term fuel % trim - Bank 1',
				'Units': '%',
				'Pattern': '^[A-Z0-9]{2} [A-Z0-9]{2} ([A-Z0-9]{2}) $',
				'Value': lambda m: (int(m.group(1),16)-128) * 100.0 / 128 },
			0x08: {
				'Name': 'Short term fuel % trim - Bank 2',
				'Units': '%',
				'Pattern': '^[A-Z0-9]{2} [A-Z0-9]{2} ([A-Z0-9]{2}) $',
				'Value': lambda m: (int(m.group(1),16)-128) * 100.0 / 128 },
			0x09: {
				'Name': 'Long term fuel % trim - Bank 2',
				'Units': '%',
				'Pattern': '^[A-Z0-9]{2} [A-Z0-9]{2} ([A-Z0-9]{2}) $',
				'Value': lambda m: (int(m.group(1),16)-128) * 100.0 / 128 },
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
				'Value': lambda m: ((int(m.group(1),16) * 256) + int(m.group(2), 16))/4.0},
			0x0D: {
				'Name': 'Vehicle speed',
				'Units': 'km/h',
				'Pattern': '^[A-Z0-9]{2} [A-Z0-9]{2} ([A-Z0-9]{2}) $',
				'Value': lambda m: int(m.group(1),16) },
			0x0E: {
				'Name': 'Timing advance',
				'Units': '* rel #1 cylinder',
				'Pattern': '^[A-Z0-9]{2} [A-Z0-9]{2} ([A-Z0-9]{2}) $',
				'Value': lambda m: (int(m.group(1),16) - 128) / 2.0 },
			0x0F: {
				'Name': 'Intake air temperature',
				'Units': '*C',
				'Pattern': '^[A-Z0-9]{2} [A-Z0-9]{2} ([A-Z0-9]{2}) $',
				'Value': lambda m: int(m.group(1),16) - 40 },
			0x10: {
				'Name': 'MAF Sensor air flow rate',
				'Units': 'grams/sec',
				'Pattern': '^[A-Z0-9]{2} [A-Z0-9]{2} ([A-Z0-9]{2}) ([A-Z0-9]{2}) $',
				'Value': lambda m: ((int(m.group(1),16) * 256) + int(m.group(2), 16))/100.0},
			0x11: {
				'Name': 'Throttle position',
				'Units': '%',
				'Pattern': '^[A-Z0-9]{2} [A-Z0-9]{2} ([A-Z0-9]{2}) $',
				'Value': lambda m: (int(m.group(1),16) * 100.0) / 255 },
			0x1F: {
				'Name': 'Run time since engine start',
				'Units': 's',
				'Pattern': '^[A-Z0-9]{2} [A-Z0-9]{2} ([A-Z0-9]{2}) ([A-Z0-9]{2}) $',
				'Value': lambda m: (int(m.group(1),16) * 256) + int(m.group(2), 16)},
			0x21: {
				'Name': 'Distance traveled with malfuction indicator lamp on',
				'Units': 'km',
				'Pattern': '^[A-Z0-9]{2} [A-Z0-9]{2} ([A-Z0-9]{2}) ([A-Z0-9]{2}) $',
				'Value': lambda m: (int(m.group(1),16) * 256) + int(m.group(2), 16)},
			0x22: {
				'Name': 'Fuel Rail Pressure (relative to manifold vacuum)',
				'Units': 'kPa',
				'Pattern': '^[A-Z0-9]{2} [A-Z0-9]{2} ([A-Z0-9]{2}) ([A-Z0-9]{2}) $',
				'Value': lambda m: (int(m.group(1),16) * 256) + int(m.group(2), 16) * 0.079},
			0x23: {
				'Name': 'Fuel Rail Pressure (diesel, or gasoline direct injection)',
				'Units': 'kPa',
				'Pattern': '^[A-Z0-9]{2} [A-Z0-9]{2} ([A-Z0-9]{2}) ([A-Z0-9]{2}) $',
				'Value': lambda m: (int(m.group(1),16) * 256) + int(m.group(2), 16) * 10},
			0x2C: {
				'Name': 'Commanded EGR',
				'Units': '%',
				'Pattern': '^[A-Z0-9]{2} [A-Z0-9]{2} ([A-Z0-9]{2}) $',
				'Value': lambda m: (int(m.group(1),16) * 100.0) / 255 },
			0x2D: {
				'Name': 'EGR Error',
				'Units': '%',
				'Pattern': '^[A-Z0-9]{2} [A-Z0-9]{2} ([A-Z0-9]{2}) $',
				'Value': lambda m: ((int(m.group(1),16) - 128) * 100.0) / 128 },
			0x2E: {
				'Name': 'Commanded evaporative purge',
				'Units': '%',
				'Pattern': '^[A-Z0-9]{2} [A-Z0-9]{2} ([A-Z0-9]{2}) $',
				'Value': lambda m: (int(m.group(1),16) * 100.0) / 255 },
			0x2F: {
				'Name': 'Fuel level input',
				'Units': '%',
				'Pattern': '^[A-Z0-9]{2} [A-Z0-9]{2} ([A-Z0-9]{2}) $',
				'Value': lambda m: (int(m.group(1),16) * 100.0) / 255 },
			0x30: {
				'Name': '# of warm-ups since codes cleared',
				'Units': '%',
				'Pattern': '^[A-Z0-9]{2} [A-Z0-9]{2} ([A-Z0-9]{2}) $',
				'Value': lambda m: int(m.group(1),16) },
			0x31: {
				'Name': 'Distance traveled since codes cleared',
				'Units': 'km',
				'Pattern': '^[A-Z0-9]{2} [A-Z0-9]{2} ([A-Z0-9]{2}) ([A-Z0-9]{2}) $',
				'Value': lambda m: (int(m.group(1),16) * 256) + int(m.group(2), 16)},
			0x33: {
				'Name': 'Barometric pressure',
				'Units': 'kPa (absolute)',
				'Pattern': '^[A-Z0-9]{2} [A-Z0-9]{2} ([A-Z0-9]{2}) $',
				'Value': lambda m: int(m.group(1),16) },
			0x42: {
				'Name': 'Control module voltage',
				'Units': 'V',
				'Pattern': '^[A-Z0-9]{2} [A-Z0-9]{2} ([A-Z0-9]{2}) ([A-Z0-9]{2}) $',
				'Value': lambda m: (int(m.group(1),16) * 256) + int(m.group(2), 16) / 1000.0},
			0x43: {
				'Name': 'Absolute load value',
				'Units': '%',
				'Pattern': '^[A-Z0-9]{2} [A-Z0-9]{2} ([A-Z0-9]{2}) ([A-Z0-9]{2}) $',
				'Value': lambda m: (int(m.group(1),16) * 256) + int(m.group(2), 16) * 100.0 / 255},
			0x44: {
				'Name': 'Fuel/Air commanded equivalence ratio',
				'Units': '',
				'Pattern': '^[A-Z0-9]{2} [A-Z0-9]{2} ([A-Z0-9]{2}) ([A-Z0-9]{2}) $',
				'Value': lambda m: (int(m.group(1),16) * 256) + int(m.group(2), 16) / 32768.0},
			0x45: {
				'Name': 'Relative throttle position',
				'Units': '%',
				'Pattern': '^[A-Z0-9]{2} [A-Z0-9]{2} ([A-Z0-9]{2}) $',
				'Value': lambda m: int(m.group(1),16) * 100.0 / 255 },
			0x46: {
				'Name': 'Ambient air temperature',
				'Units': '*C',
				'Pattern': '^[A-Z0-9]{2} [A-Z0-9]{2} ([A-Z0-9]{2}) $',
				'Value': lambda m: int(m.group(1),16) - 40 },
			0x47: {
				'Name': 'Absolute throttle position B',
				'Units': '%',
				'Pattern': '^[A-Z0-9]{2} [A-Z0-9]{2} ([A-Z0-9]{2}) $',
				'Value': lambda m: int(m.group(1),16) * 100.0 / 255 },
			0x48: {
				'Name': 'Absolute throttle position C',
				'Units': '%',
				'Pattern': '^[A-Z0-9]{2} [A-Z0-9]{2} ([A-Z0-9]{2}) $',
				'Value': lambda m: int(m.group(1),16) * 100.0 / 255 },
			0x49: {
				'Name': 'Absolute throttle position D',
				'Units': '%',
				'Pattern': '^[A-Z0-9]{2} [A-Z0-9]{2} ([A-Z0-9]{2}) $',
				'Value': lambda m: int(m.group(1),16) * 100.0 / 255 },
			0x4A: {
				'Name': 'Absolute throttle position E',
				'Units': '%',
				'Pattern': '^[A-Z0-9]{2} [A-Z0-9]{2} ([A-Z0-9]{2}) $',
				'Value': lambda m: int(m.group(1),16) * 100.0 / 255 },
			0x4B: {
				'Name': 'Absolute throttle position F',
				'Units': '%',
				'Pattern': '^[A-Z0-9]{2} [A-Z0-9]{2} ([A-Z0-9]{2}) $',
				'Value': lambda m: int(m.group(1),16) * 100.0 / 255 },
			0x4C: {
				'Name': 'Commanded throttle actuator',
				'Units': '%',
				'Pattern': '^[A-Z0-9]{2} [A-Z0-9]{2} ([A-Z0-9]{2}) $',
				'Value': lambda m: int(m.group(1),16) * 100.0 / 255 },
			0x4D: {
				'Name': 'Time run with MIL on',
				'Units': 'minutes',
				'Pattern': '^[A-Z0-9]{2} [A-Z0-9]{2} ([A-Z0-9]{2}) ([A-Z0-9]{2}) $',
				'Value': lambda m: (int(m.group(1),16) * 256) + int(m.group(2), 16)},
			0x4E: {
				'Name': 'Time since codes cleared',
				'Units': 'minutes',
				'Pattern': '^[A-Z0-9]{2} [A-Z0-9]{2} ([A-Z0-9]{2}) ([A-Z0-9]{2}) $',
				'Value': lambda m: (int(m.group(1),16) * 256) + int(m.group(2), 16)},
			0x52: {
				'Name': 'Fuel ethanol percentage',
				'Units': '%',
				'Pattern': '^[A-Z0-9]{2} [A-Z0-9]{2} ([A-Z0-9]{2}) $',
				'Value': lambda m: int(m.group(1),16) * 100.0 / 255 },
			0x53: {
				'Name': 'Absolute evaporative system vapor pressure',
				'Units': 'kPa',
				'Pattern': '^[A-Z0-9]{2} [A-Z0-9]{2} ([A-Z0-9]{2}) ([A-Z0-9]{2}) $',
				'Value': lambda m: ((int(m.group(1),16) * 256) + int(m.group(2), 16)) / 200.0},
			0x54: {
				'Name': 'Relative evaporative system vapor pressure',
				'Units': 'kPa',
				'Pattern': '^[A-Z0-9]{2} [A-Z0-9]{2} ([A-Z0-9]{2}) ([A-Z0-9]{2}) $',
				'Value': lambda m: ((int(m.group(1),16) * 256) + int(m.group(2), 16)) - 32767},
			0x59: {
				'Name': 'Absolute fuel rail pressure',
				'Units': 'kPa',
				'Pattern': '^[A-Z0-9]{2} [A-Z0-9]{2} ([A-Z0-9]{2}) ([A-Z0-9]{2}) $',
				'Value': lambda m: ((int(m.group(1),16) * 256) + int(m.group(2), 16)) * 10},
			0x5A: {
				'Name': 'Relative accelerator pedal position',
				'Units': '%',
				'Pattern': '^[A-Z0-9]{2} [A-Z0-9]{2} ([A-Z0-9]{2}) $',
				'Value': lambda m: int(m.group(1),16) * 100.0 / 255 },
			0x5B: {
				'Name': 'Hybrid battery pack remaining life',
				'Units': '%',
				'Pattern': '^[A-Z0-9]{2} [A-Z0-9]{2} ([A-Z0-9]{2}) $',
				'Value': lambda m: int(m.group(1),16) * 100.0 / 255 },
			0x5C: {
				'Name': 'Engine oil temperature	',
				'Units': '*C',
				'Pattern': '^[A-Z0-9]{2} [A-Z0-9]{2} ([A-Z0-9]{2}) $',
				'Value': lambda m: int(m.group(1),16) - 40 },
		}
	}
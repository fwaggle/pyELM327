"""
Python module presenting an API to an ELM327 serial interface
(C) 2015 Jamie Fraser <fwaggle@fwaggle.org>
http://github.com/fwaggle/pyELM327

Please see License.txt and Readme.md.
"""

import serial, time, pprint, re
import pids

pidlist = pids.__pids


class ELM327(object):
	"""
	ELM327 Class

	Meta-class for abstracting ELM327 device.
	"""
	__ser = None # pySerial object.
	__readBuffer = ''
	__debug = 0

	id = None


	def __init__(self, port, debug=0, baud=38400, rtscts=0, xonxoff=0):
		self.__debug = debug
		self.__ser = serial.Serial(port, baud, timeout=5, rtscts=rtscts, xonxoff=xonxoff)
		self.reset()

	def reset(self):
		"""
		Try to put the ELM327 device into a known state, by resetting
		it then turning off echos.
		"""

		# 'ATZ' will, depending on the status of the device's echo setting
		# return either just the device ID, or 'ATZ\r' followed by the ID.
		self.write('ATZ', nowait=1)
		self.id = self.expect('^ELM327') # Expecting 'ELM327 v1.5'

		# turn off echos
		self.write('ATE0')
		self.expect('^(>)?OK') # should be 'OK'
		self.expect('>')

		# Set protocol == AUTO for a sensible default
		# My holden is then AUTO, SAE J1850 VPW
		self.write('ATSP 0')
		self.expect('^(>)?OK')

	def tryBaudrate(self, rate=38400):
		"""
		Try a faster baud rate for the PC->ELM327 connection. Depending on your hardware,
		this may not work - for example Bluetooth adaptors are notoriously shit.

		Note that you can't specify 9600 baud - that requires a divisor higher than FF.

		If your device starts in 9600 baud (a hardware pin setting), simply init the ELM327
		class with baudrate=9600 and if higher baud rates don't work reset it with ATZ. 
		If it starts in 38400 baud, and you don't get a stable connection, throw the device
		away and buy a better one.
		"""
		
		# Select appropriate divisor - higher rates may cause a '?' response from ELM
		if rate == 38400:
			divisor = '69'
		elif rate == 57600:
			divisor = '45'
		elif rate == 115200:
			divisor = '23'
		elif rate == 500000:
			divisor = '08'
		elif rate == 666700:
			divisor = '06'
		else:
			raise Exception('Baud rate not implemented')

		# set the baud rate timeout - my python code isn't fast enough for 75ms
		# without getting the response in the old baud rate
		self.write('ATBRT 00')
		result = self.expect('^(>)?OK')

		# try to set the baud rate to 115200
		self.write('ATBRD ' + divisor)
		result = self.expect('^(>)?OK')
		print "result: %s" % result
		self.baudrate = rate
		
		# we should get ELM327 at the new baud rate if it worked.
		result = self.expect('^ELM327')

		print "Res: %s" % result

		# if we get header at new baud rate, ELM is expecting CR at new baud rate.
		self.write('', 1)
		print "result: %s" % result

	@property
	def baudrate(self):
	    return self.__ser.baudrate

	@baudrate.setter
	def baudrate(self, rate):
		self.__ser.baudrate = rate

	def close(self):
		self.__ser.close()

	def fetchProtocol(self):
		"""
		Describe the Protocol used by the ELM327, most of the time this will return AUTO
		for no good reason.
		"""
		self.write('ATDP')
		result = self.expect('^>?(.+)$')
		return result

	def empty(self):
		"""
		Empty the read buffer - ensures we don't leave data in the way
		if a cheap-shit ELM327 clone doesn't respond within 1 second.

		This function is deprecated as our buffer code is a lot nicer now.
		"""
		self.__ser.flushInput()
		self.__readBuffer = '>' # kludge, I can't find a noop in the ELM327 commandset

	def __enter__(self):
		return self

	def __exit__(self, exception_type, exception_value, traceback):
		self.close()

	def write(self, data, nowait=None):
		"""
		Send raw data to the ELM327. For most features this shouldn't be necessary.
		"""

		if self.__debug:
			print (">>> %s" % data)

		if nowait == None:
			if self.__debug:
				print "DEBUG: Waiting for '>'"
			self.expect('>')

		self.__ser.flushOutput()
		self.__ser.write(data + '\r')

	def expect(self, pattern):
		if self.__debug:
			print "Expect: '%s'" % pattern
		while True:
			n = self.__ser.inWaiting()
			if n > 0:
				self.__readBuffer += self.__ser.read(n)

			if self.__readBuffer.count('\r') > 0:
				lines = self.__readBuffer.split('\r')

				if self.__debug:
					pprint.pprint(lines)

				for l in lines:
					# drop each line from the read buffer as we process it.
					self.__readBuffer = self.__readBuffer[self.__readBuffer.find('\r')+1:]

					if re.search('^UNABLE TO CONNECT', l):
						raise Exception('UNABLE TO CONNECT')
					if re.search('^NO DATA', l):
						return None
					if re.search('^STOPPED', l):
						raise Exception('STOPPED')
					if re.search('^(>)?\?', l):
						raise Exception('UNKNOWN COMMAND')
					if re.search(pattern, l):
						return l
			
			if (self.__readBuffer == '>' or self.__readBuffer == '\r>') and pattern == '>':
				self.__readBuffer = ''
				return '>'

			time.sleep(0.1)

	def fetchBatteryLevel(self):
		"""
		Fetch the battery level from the ELM327.
		"""
		self.write('AT RV')
		result = self.expect('^[0-9\.]+V')
		return result

	def fetchLiveData(self, reqPID):
		"""
		Fetch Live Data at the requested PID from ECU.


		"""
		global pidlist # Nasty, but I don't know a better way yet
		
		if reqPID not in pidlist[0x01]:
			raise KeyError('Unsupported PID 0x%02x' % reqPID)

		pid = pidlist[0x01][reqPID]

		# Request the data
		self.write('01%02x1' % reqPID)
		result = self.expect('^41 ')

		# Test Data
		# result = '41 0C 0E 5A '

		if result == None:
			val = 'NO DATA'
		else:
			# Apply the pattern to the response
			m = re.match(pid['Pattern'], result)
			if m == None or m.group(0) == None:
				raise Exception('Malformed response')

			val = pid['Value'](m)
		
		return {'pid': reqPID,
				'value': val,
				'name': pid['Name'],
				'units': pid['Units']}

	def fetchDTCs(self):
		"""
		Fetch Diagnostic Trouble Codes from the ECU.

		Currently this function prints out the count of DTCs and the status of the
		MIL, but this behaviour will change eventually.
		"""
		classes = {
			'0': 'P0',
			'1': 'P1',
			'2': 'P2',
			'3': 'P3',
			'4': 'C0',
			'5': 'C1',
			'6': 'C2',
			'7': 'C3',
			'8': 'B0',
			'9': 'B1',
			'A': 'B2',
			'B': 'B3',
			'C': 'U0',
			'D': 'U1',
			'E': 'U2',
			'F': 'U3',
		}

		self.write('0101')
		result = self.expect('^41 01')

		# Test data
		#result = '41 01 82 07 65 04 '

		if result == None:
			return 'NO DATA'

		m = re.match('^41 01 ([A-Z0-9]{2})', result)
		if m == None or m.group(0) == None:
			raise Exception('Malformed response')

		cel = int(m.group(1), 16) & 0x80
		count = int(m.group(1), 16) - cel
		cel = cel / 0x80

		print ("CEL: %d DTC Count: %d" % (cel, count))

		if count < 1:
			return

		self.write('03')
		result = self.expect('^43 ')

		# Test data
		#result = '43 01 33 81 34 00 00 '

		pprint.pprint(result)

		m = re.match('^43 (([A-Z0-9]{2} [A-Z0-9]{2} )+)', result)
		if m == None or m.group(0) == None:
			return

		#print m.group(1)

		"""
		NOTE: I don't actually know if the last three digits of the DTC
		are to be interpreted as decimals or HEX, and the ELM327 datasheet
		is ambiguous. Assuming the former for the time being.
		"""

		dtcs = re.findall('([A-Z0-9]{2} [A-Z0-9]{2}) ', m.group(1))
		ret = []
		for dtc in dtcs:
			if dtc != '00 00':
				cls = dtc[0:1]
				ret.append("%s%s" % (classes[cls], dtc[1:].replace(' ', '')))

		return ret

	def clearDTCs(self, confirm=0):
		"""
		Clear Diagnostic Trouble Codes from the ECU.

		The software is responsible for confirming that this is what the user
		actually intends to do - you must pass a "confirm" argument to get it to
		clear the codes, otherwise an exception is raised.
		"""
		if confirm:
			self.write('04')
			result = self.expect('^44')
			return result
		else:
			raise Exception('Confirm clear DTCs?')

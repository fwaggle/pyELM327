"""
Python module presenting an API to an ELM327 serial interface
(C) 2015 Jamie Fraser <fwaggle@fwaggle.org>
http://github.com/fwaggle/pyELM327

Please see License.txt and Readme.md.
"""

import serial, time, pprint, re
import pids

pidlist = pids.__pids

class ELM327:
	__ser = None # pySerial object.
	readBuffer = ''
	id = None

	def __init__(self, port, baud=38400, rtscts=0, xonxoff=0):
		self.__ser = serial.Serial(port, baud, timeout=5, rtscts=rtscts, xonxoff=xonxoff)

		"""
			Try to put the ELM327 device into a known state, by resetting
			it then turning off echos.

			'ATZ' will, depending on the status of the device's echo setting
			return either just the device ID, or 'ATZ\r' followed by the ID.
		"""
		self.write('ATZ')
		self.id = self.expect('^ELM327') # Expecting 'ELM327 v1.5'
		self.empty()

		# turn off echos
		self.write('ATE0')
		self.expect('^OK') # should be 'OK'
		self.empty()

		# Set protocol == AUTO for a sensible default
		self.write('ATSP 0')
		self.expect('^OK')
		self.empty()

	def close(self):
		self.__ser.close()

	def empty(self):
		"""
			empties the read buffer - ensures we don't leave data in the way
			if a cheap-shit ELM327 clone doesn't respond within 1 second.
		"""
		self.__ser.flushInput()
		self.readBuffer = ''

	def __enter__(self):
		return self

	def __exit__(self, exception_type, exception_value, traceback):
		self.close()

	def write(self, data):
		# print (">>> %s" % data)
		self.__ser.flushOutput()
		self.__ser.write(data + '\r\n')

	def expect(self, pattern):
		while True:
			n = self.__ser.inWaiting()
			if n > 0:
				self.readBuffer += self.__ser.read(n)
				if self.readBuffer.count('\r') > 0:
					lines = self.readBuffer.split('\r')
					# pprint.pprint(lines)
					for l in lines:
						if re.search('^UNABLE TO CONNECT', l):
							self.readBuffer = ''
							return None
						if re.search('^NO DATA', l):
							self.readBuffer = ''
							return None
						if re.search('^STOPPED', l):
							self.readBuffer = ''
							return None
						if re.search(pattern, l):
							self.readBuffer = ''
							return l
					self.readBuffer = ''

			time.sleep(0.1)

	def fetchLiveData(self, reqPID):
		global pidlist # Nasty, but I don't know a better way yet
		
		if reqPID not in pidlist[0x01]:
			raise KeyError('Unsupported PID 0x%02x' % reqPID)

		pid = pidlist[0x01][reqPID]

		# Request the data
		self.write('01%02x' % reqPID)
		result = self.expect('^41 ')

		# Test Data
		# result = '41 0C 0E 5A '

		if result == None:
			return 'NO DATA'

		# Apply the pattern to the response
		m = re.match(pid['Pattern'], result)
		if m.group(0) == None:
			raise Exception('Malformed response')

		val = pid['Value'](m)
		
		return {'pid': reqPID,
				'value': val,
				'name': pid['Name'],
				'units': pid['Units']}

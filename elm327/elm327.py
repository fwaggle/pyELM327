"""
Python module presenting an API to an ELM327 serial interface
(C) 2015-2017 James Fraser <fwaggle@fwaggle.org>
http://github.com/fwaggle/pyELM327

Please see License.txt and Readme.md.
"""

import serial, time, pprint, re

class ELM327(object):
	"""
	ELM327 Class

	Meta-class for abstracting ELM327 device.
	"""

	def __init__(self, port, debug=0, baud=38400, rtscts=0, xonxoff=0, coldstart=False):
		"""Initialize the ELM327 device."""
		self.__debug = debug
		self.id = None
		self.version = 'UNKNOWN'
		self.__readBuffer = ''
		self.__echo = None
		self.__allowlong = None

		self.__ser = serial.Serial(port, baud, timeout=5, rtscts=rtscts, xonxoff=xonxoff)

		# Look for the device, and initialize it
		self.findDevice()

		self.echo = False
		self.allowlong = False

		# Turn off spaces to speed up data transfer
		self.write('ATS0')
		self.expect('^OK', 500)
		self.expectDone()

		# Ask it to identify itself.
		self.write('ATI')
		version = self.expect('^ELM327 v([0-9\.]+)', 500)
		self.version = version.group(1) # TODO: Error checking
		self.expectDone()


	def findDevice(self, retries=2):
		for attempt in range(retries + 1):
			# Send the command twice, because who knows what garbage was on the 
			# line buffer before we sent the command, due to possibly wrong rate?
			# 
			# Also, we send "AT " because an empty newline repeats the previous command,
			# and we have no way of knowing what that was. "AT " seems pretty safe.
			# It should emit a "?" in response.
			self.write('AT ')
			self.write('AT ')
			self.expect('^\?', 1000)

			# Clear the input buffer and try one more time.
			# We should get one ? and a > prompt.
			self.__ser.flushInput()
			self.write('AT ')
			self.expect('^\?', 1000)
			self.expectDone()
			return True

		# If we get here, the ELM327 is not responding correctly and retries ran out.
		return False

	def close(self):
		"""Close the serial port."""
		self.__ser.close()

	def fetchBatteryLevel(self):
		self.write('ATRV')
		result = self.expect('^([0-9\.]+)V', 5000)
		if result != None:
			return result.group(1)
		return None

	# Read and write functions
	##########################
	def write(self, data):
		if self.__debug:
			print(">>> %s" % data)

		# Append carriage return then convert to ASCII
		data = (data + '\r').encode('ascii')

		self.__ser.flushOutput()
		self.__ser.write(data)

	def expectDone(self, timeout=None):
		self.expect('>', timeout)
		self.__readBuffer = ''
		self.__ser.flushInput()


	def expect(self, pattern, timeout=None):
		"""
		expect() - wait for a response from the device matching a regular expression
		returns: a regular expression match object, or "None" if timeout is reached.
		"""
		start = time.time()

		if self.__debug:
			print("Expect: '%s'" % pattern)

		while True:
			# check if timeout is up
			if timeout:
				if ((time.time() - start) * 1000) > timeout:
					return None

			# check for new data on serial port
			n = self.__ser.inWaiting()
			if n > 0:
				self.__readBuffer += self.__ser.read(n).decode('ascii')

			# examine buffer
			if self.__readBuffer.count('\r') > 0:
				lines = self.__readBuffer.split('\r')

				if self.__debug:
					pprint.pprint(lines)

				for l in lines:
					# Drop each line from the read buffer as we process it.
					self.__readBuffer = self.__readBuffer[self.__readBuffer.find('\r')+1:]

					# Search for various errors.
					if re.search('^UNABLE TO CONNECT', l):
						raise Exception('UNABLE TO CONNECT')
					if re.search('^NO DATA', l):
						return None
					if re.search('^STOPPED', l):
						raise Exception('STOPPED')
					if (pattern != '^\?' and re.search('^\?', l)):
						raise Exception('UNKNOWN COMMAND')

					# Now search for the pattern
					match = re.search(pattern, l) 
					if match:
						return match

			# expect('>') is a special case, because it will not end with '\r'
			if (self.__readBuffer == '>' or self.__readBuffer == '\r>') and pattern == '>':
				self.__readBuffer = ''
				return '>'

			# wait 10ms and try again
			time.sleep(0.01)


	# Get/Set the baud rate of the serial device.
	#############################################
	@property
	def baudrate(self):
	    return self.__ser.baudrate

	@baudrate.setter
	def baudrate(self, rate):
		self.__ser.baudrate = rate


	@property
	def echo(self):
		return self.__echo

	@echo.setter
	def echo(self, enabled):
		self.write('ATE' + ('1' if enabled else '0'))
		self.expect('OK', 500)
		self.expectDone()
		self.__echo = enabled

	@property
	def allowlong(self):
		return self.__allowlong

	@echo.setter
	def allowlong(self, enabled):
		if enabled:
			self.write('ATAL')
		else:
			self.write('ATNL')

		self.expect('OK', 500)
		self.expectDone()
		self.__allowlong = enabled

	# Allow object to be used with python's "with" feature
	######################################################
	def __enter__(self):
		return self

	def __exit__(self, exception_type, exception_value, traceback):
		self.close()

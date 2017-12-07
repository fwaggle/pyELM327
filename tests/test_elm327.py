#! /usr/bin/python3

import unittest, time, sys
sys.path.append(".")
sys.path.append("..")
from elm327 import elm327

class TestELM327Lib(unittest.TestCase):
	def test_init(self):
		with elm327.ELM327('/dev/ttyUSB0', baud=38400, debug=False) as elm:
			self.assertEqual('1.5', elm.version)

	def test_serial_baudrate(self):
		with elm327.ELM327('/dev/ttyUSB0', baud=38400) as elm:
			# We specified a baud rate when we instantiated, check it's correct.
			self.assertEqual(38400, elm.baudrate)

			# Now check it changes ok.
			elm.baudrate=9600
			self.assertEqual(9600, elm.baudrate)

			# Check invalid assignments raise appropriate exceptions
			with self.assertRaises(ValueError):
				elm.baudrate='invalid'

if __name__ == '__main__':
    unittest.main()

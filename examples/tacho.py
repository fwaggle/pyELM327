#! /usr/bin/python

import time, sys
sys.path.append(".")
sys.path.append("..")
from elm327 import elm327

with elm327.ELM327('/dev/ttyUSB0') as elm:

	print("Device reports as: %s" % elm.id)
	
	while True:
		for pid in [0x0c, 0x11]:
			try:
				data = elm.fetchLiveData(pid)
			except Exception as e:
				if e == 'STOPPED':
					elm.reset()
				else:
					raise e
			else:
				print("%s: %5.2f" % (data['name'], data['value']))
				#time.sleep(0.05)

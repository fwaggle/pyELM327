#! /usr/bin/python

import time, sys
sys.path.append(".")
sys.path.append("..")
from elm327 import elm327, pids

with elm327.ELM327('/dev/ttyUSB0') as elm:

	print("Device reports as: %s" % elm.id)

	while True:
		# Iteratively fetch all PIDs in Mode 01
		for pid in pids.__pids[0x01]:
			try:
				res = elm.fetchLiveData(pid)
				if res is dict:
					print("%s: %s %s" % (res['name'], res['value'], res['units']))
			except Exception as e:
				if e == 'STOPPED':
					elm.reset()
				else:
					print e
#			time.sleep(0.5) # May need adjusting, depending on your ELM327
		print("")

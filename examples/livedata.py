#! /usr/bin/python

import time, sys
sys.path.append(".")
sys.path.append("..")
from elm327 import elm327, pids

with elm327.ELM327(2) as elm:

	print("Device reports as: %s" % elm.id)

	print elm.fetchDTCs()

	while True:
		# Iteratively fetch all PIDs in Mode 01
		for pid in pids.__pids[0x01]:
			res = elm.fetchLiveData(pid)
			print("%s: %s %s" % (res['name'], res['value'], res['units']))
			time.sleep(1) # May need adjusting, depending on your ELM327
		print("")

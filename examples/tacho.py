#! /usr/bin/python

import time, sys
sys.path.append(".")
sys.path.append("..")
from elm327 import elm327

with elm327.ELM327(2) as elm:

	print("Device reports as: %s" % elm.id)
	while True:
		print elm.fetchLiveData(0x0c) # 0x0C is Engine RPM
		time.sleep(1)

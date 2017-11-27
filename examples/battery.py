#! /usr/bin/python3

import time, sys
sys.path.append(".")
sys.path.append("..")
from elm327 import elm327

with elm327.ELM327('/dev/ttyUSB0') as elm:
	print(elm.fetchBatteryLevel())

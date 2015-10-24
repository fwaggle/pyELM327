# pyELM327 - A Python interface to Generic OBD2 Devices

Frustrated with the quality of free OBD2 software, I decided to write my own.
This involved learning how the ELM327 interface works, and in the meantime I
figured I'd simply provide an API to access the ELM327 device
programmatically, which I can then wrap a UI around.

**Note**: This is a work in progress, please don't expect it to be complete.

It's also very poorly tested, using only the platforms and vehicles I had
available. At this stage, that consists of:

* 1999 Holden Commodore VT Series II (LS1 Engine)
* 2007 Holden Cruze

## Requirements

* ELM327 device - Generic devices vary vastly in quality, so compatibility
is not guaranteed.
* Python 2.7 or later (3.x support not guaranteed)
* [pySerial](http://pyserial.sourceforge.net/)

## Using

pyELM327 supports Python's Context Manager, so you can do stuff like this:

```
import elm327

with elm327.ELM327(2) as elm:
	print elm.fetchBatteryLevel()
```

The argument 2 is the port, per the pySerial specifications (COM3 in this
case). On Linux replace 2 with '/dev/ttyUSB0'. You can also specify the baud rate and other serial port options.

Other examples can be found in `examples/`

## Known Bugs and Issues

* I've changed the write() routine to wait for a '>' before sending, but this may have broken something. For example, turning off echos breaks things for some commands, so I've disabled that and we just eat the echos now.

* We don't cope with changing baudrates terribly well at all - need support for polling the baudrate so we can reset a device with a non-default baud rate.

* Haven't tested DTC retrieval, because I haven't yet managed to throw a code on any of my cars. I might just unplug the MAF.

* expect() can't deal with failure - it'll simply wait forever for the correct response. This needs fixing pronto as it's blocking other features.

* Need to implement proper exceptions.

* Documentation is appalling.

## Sources and Attributions

* http://elmelectronics.com/DSheets/ELM327DS.pdf
* https://www.sparkfun.com/datasheets/Widgets/ELM327_AT_Commands.pdf
* http://www.obdsol.com/knowledgebase/obd-software-development/reading-real-time-data/
* https://en.wikipedia.org/wiki/OBD-II_PIDs
* https://en.wikipedia.org/wiki/ISO_15765-2

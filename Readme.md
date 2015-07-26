# pyELM327 - A Python interface to Generic OBD2 Devices

**Note: This is a work in progress, please don't expect it to be complete.

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
	elm.write('ATZ')
```

The argument 2 is the port, per the pySerial specifications (COM3 in this
case). You can also specify the baud rate and other serial port options.

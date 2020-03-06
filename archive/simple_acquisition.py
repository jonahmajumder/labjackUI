import u3
from LabJackPython import NullHandleException
import os,sys
import usb

# The LabJack vendor ID is 0x0CD5. The product ID for the U3 is 0x0003.
VENDOR_ID = 0x0CD5
PRODUCT_ID = 0x0003

dictU3 = {
	'idVendor': VENDOR_ID,
	'idProduct': PRODUCT_ID
}

def u3connected():
	dev = usb.core.find(**dictU3)
	if dev is None:
		return False
	else:
		return True

try:
	dev = u3.U3()
	info = dev.configU3()
	print('Connected to {} device.'.format(info['DeviceName']))
except NullHandleException:
	print('No devices detected.')
	sys.exit(0)

# print([l for l in f.getvalue()])


# find_u3.py

import usb

VENDOR_ID = 0x0CD5
PRODUCT_ID = 0x0003

idDict = {
	'idVendor': VENDOR_ID,
	'idProduct': PRODUCT_ID
}


print(repr(usb.core.find(**idDict)))
# standard imports
import weakref
import gc

# third party imports
from u3 import U3
from LabJackPython import NullHandleException
from LabJackPython import deviceCount
from LabJackPython import listAll, isHandleValid

# The LabJack vendor ID is 0x0CD5. The product ID for the U3 is 0x0003.
VENDOR_ID = 0x0CD5
PRODUCT_ID = 0x0003
DEVICE_TYPE = 3

class DeviceNotPresentError(Exception):
	pass

class DeviceAccessError(Exception):
	pass

def deletion_notifier(ref):
	print('Deleting {}.'.format(ref))

class MyU3(U3):
	instances = []
	verbose = True # if it's a class variable, default is public

	def __init__(self):
		self.check_connected()

		super().__init__(autoOpen=False) # do that "manually"
		self.__class__.instances.append(weakref.ref(self))
		self.open()

		if self.is_open():
			self.getCalibrationData()
			self.properties = self.configU3()


	# def instance_index(self):
	# 	return self.__class__.instances.index(self)

	def open(self):
		if not self.is_open():
			if not self.__class__.any_open():
				try:
					super().open() # "super()" needed to avoid recursion
				except NullHandleException:
					self.alert('Unable to open device, possibly because it is open in another process.')
			else:
				self.alert('Another open instance already exists. Device not opened.')
		else:
			self.alert('Device is already open.')

	# @classmethod
	def close(self):
		if self.is_open():
			super().close() # "super()" needed to avoid recursion
		else:
			# self.alert('Device is already closed.')
			pass

	def is_open(self):
		return bool(isHandleValid(self.handle))

	def check_connected(self):
		if not self.is_connected():
			raise(DeviceNotPresentError('No U3 device detected over USB.'))

	def alert(self, message):
		if self.verbose:
			print(message)

	@staticmethod # argument is uninitialized version of class
	def is_connected():
		return deviceCount(DEVICE_TYPE) > 0

	@classmethod
	def any_open(cls):
		return any([ref().is_open() for ref in cls.instances])

	@classmethod
	def cleanup_instances(cls):
		cls.instances = list(filter(lambda ref: ref() != None, cls.instances))

	@classmethod
	def close_all(cls):
		cls.cleanup_instances()
		[ref().close() for ref in cls.instances]



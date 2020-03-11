# standard imports
import weakref

# third party imports
import u3
from LabJackPython import deviceCount, listAll, isHandleValid, NullHandleException

# The LabJack vendor ID is 0x0CD5. The product ID for the U3 is 0x0003.
VENDOR_ID = 0x0CD5
PRODUCT_ID = 0x0003
DEVICE_TYPE = 3

'''
DEFINITIONS:
    - (io) type: analog (1) or digital (0)
        - set/retrieved with configIO method (as kwargs/dict)
    - state: high (1) or low (0)
        - for digital pins (returns error when done on pin configured as analog)
        - set/retrieved with feedback commands (Bit/Port)State(Read/Write)
    - direction: output (1) or input (2)
        - for digital pins, (returns error when done on pin configured as analog)
        - set/retrieved with feedback commands (Bit/Port)Dir(Read/Write)

'''

class DeviceNotPresentError(Exception):
    pass

class DeviceAccessError(Exception):
    pass

def deletion_notifier(ref):
    print('Deleting {}.'.format(ref))

class MyU3(u3.U3):
    instances = []
    verbose = True

    def __init__(self, *args, **kwargs):
        self.check_connected()

        u3.U3.__init__(self, False, False, **kwargs)
        self.instances.append(weakref.ref(self))
        self.open()

        if self.is_open():
            self.getCalibrationData()
            self.properties = self.configU3()

            self.isHV = self.properties['DeviceName'].endswith('HV')

    def open(self):
        if not self.is_open():
            if not self.any_open():
                try:
                    u3.U3.open(self) # "super()" needed to avoid recursion
                except NullHandleException:
                    self.alert('Unable to open device, possibly because it is open in another process.')
            else:
                self.alert('Another open instance already exists. Device not opened.')
        else:
            self.alert('Device is already open.')

    def alert(self, message):
        if self.verbose:
            print(message)

    # -------------------- DEVICE OPEN/CLOSE METHODS --------------------

    # @classmethod
    def close(self):
        if self.is_open():
            u3.U3.close(self)
        else:
            # self.alert('Device is already closed.')
            pass

    @classmethod
    def close_all(cls):
        cls.cleanup_instances()
        [ref().close() for ref in cls.instances]

    def is_open(self):
        return bool(isHandleValid(self.handle))

    def check_connected(self):
        if not self.is_connected():
            raise(DeviceNotPresentError('No U3 device detected over USB.'))

    @staticmethod # argument is uninitialized version of class
    def is_connected():
        return deviceCount(DEVICE_TYPE) > 0

    @classmethod
    def any_open(cls):
        return any([ref().is_open() for ref in cls.instances])

    @classmethod
    def cleanup_instances(cls):
        cls.instances = list(filter(lambda ref: ref() != None, cls.instances))


    # -------------------- GENERAL DEVICE COMMUNICATION --------------------

    def _feedback_command(self, command):
        resp, = self.getFeedback(command)
        return resp

    @staticmethod
    def int_to_bitarray(uint, bits=8):
        # this is for unsigned ints of course
        assert isinstance(uint, int) and isinstance(bits, int)
        assert uint >= 0 and uint < 2**bits - 1
        string = '{{0:0{}b}}'.format(bits).format(uint)
        return [bool(int(d)) for d in string]

    # -------------------- CONFIG COMMANDS --------------------

    def get_io_types(self):
        pass




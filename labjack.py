# standard imports
import weakref
import time

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
    - direction: output (1) or input (0)
        - for digital pins, (returns error when done on pin configured as analog)
        - set/retrieved with feedback commands (Bit/Port)Dir(Read/Write)
    - state: high (1) or low (0)
        - for digital pins (returns error when done on pin configured as analog)
        - set/retrieved with feedback commands (Bit/Port)State(Read/Write)

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
    isHV = True

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

    def flashLED(self, t=0.25):
        if not self.ledState:
            self.toggleLED()
        self.toggleLED()
        time.sleep(t)
        self.toggleLED()
        time.sleep(t)
        self.toggleLED()
        time.sleep(t)
        self.toggleLED()
                

    @staticmethod
    def int_to_bitarray(uint, bits=8):
        # this is for unsigned ints of course
        assert isinstance(uint, int) and isinstance(bits, int)
        assert uint >= 0 and uint < 2**bits
        string = '{{0:0{}b}}'.format(bits).format(uint)
        bools = [bool(int(d)) for d in string]
        bools.reverse()
        return bools

    # -------------------- CONFIG COMMANDS --------------------

    @classmethod
    def channelList(cls):
        channels = []
        if cls.isHV:
            channels.extend([['AIN{}'.format(i), 'analog'] for i in range(4)])
        else:
            channels.extend([['FIO{}'.format(i), None] for i in range(4)])
        channels.extend([['FIO{}'.format(i), None] for i in range(4,8)])
        channels.extend([['EIO{}'.format(i), None] for i in range(8)])
        channels.extend([['CIO{}'.format(i), 'digital'] for i in range(4)])

        return channels

    def getIOstates(self):
        '''
        return a tuple of 3 booleans for each channel, which represent:
            - type: analog (in) (True) or digital (False)
            - digital direction: output (True) or input (False)
            - digital state: high (True) or low (False)
        '''
        adprops = self.configIO()
        dirs = self._feedback_command(u3.PortDirRead())
        states = self._feedback_command(u3.PortStateRead())

        channelSettings = []

        fiotypes = self.int_to_bitarray(adprops['FIOAnalog'])
        fiodirs = self.int_to_bitarray(dirs['FIO'])
        fiostates = self.int_to_bitarray(states['FIO'])
        
        for tup in zip(fiotypes, fiodirs, fiostates):
            channelSettings.append(tup)

        eiotypes = self.int_to_bitarray(adprops['EIOAnalog'])
        eiodirs = self.int_to_bitarray(dirs['EIO'])
        eiostates = self.int_to_bitarray(states['EIO'])

        for tup in zip(eiotypes, eiodirs, eiostates):
            channelSettings.append(tup)

        ciotypes = 4 * [False] # these cannot be analog
        ciodirs = self.int_to_bitarray(dirs['CIO'], bits=4)
        ciostates = self.int_to_bitarray(states['CIO'], bits=4)

        for tup in zip(ciotypes, ciodirs, ciostates):
            channelSettings.append(tup)

        return channelSettings

    def allInputs(self):
        '''
        identify each channel as either some kind of input (analog or digital) or not
        this can (for example) determine which channels need to be polled for changes
        '''
        inputList = []
        for i, (isAnalog, isOutput, isHigh) in enumerate(self.getIOstates()):
            if isAnalog or not isOutput:
                inputList.append(i)

        return inputList

    def setChannelType(self, channelNum, isAnalog):
        # print('Setting channel {0} to analog state {1}'.format(channelNum, isAnalog))
        if isAnalog:
            self.configAnalog(channelNum)
        else:
            self.configDigital(channelNum)

    def setChannelDir(self, channelNum, isOutput):
        # print('Channel {0} set to output: {1}'.format(channelNum, isOutput))
        if isOutput:
            self.setDOState(channelNum, self.getFIOState(channelNum))
        else:
            self.getDIState(channelNum)

    def setChannelOutputState(self, channelNum, isHigh):
        self.setDOState(channelNum, int(bool(isHigh)))




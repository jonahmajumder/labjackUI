
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget
from PyQt5 import uic

from LabJackPython import deviceCount, listAll
from labjack import MyU3

Form, Base = uic.loadUiType('connect.ui')

class ConnectPanel(Base, Form):
    childNames = ['deviceComboBox', 'propertyViewer']

    deviceType = 3

    deviceOpened = QtCore.pyqtSignal(MyU3)

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        # self.groupButtons()


        self.setupUi(self)
        self.gatherChildren()

        self.setupComboBox()

        self.propertyViewer.setColumnCount(2)
        self.propertyViewer.setHorizontalHeaderItem(0, QtWidgets.QTableWidgetItem('Property'))
        self.propertyViewer.setHorizontalHeaderItem(1, QtWidgets.QTableWidgetItem('Value'))
        self.propertyViewer.horizontalHeader().setStretchLastSection(True)

        self.connectButtons()

    def gatherChildren(self):
        for name in self.childNames:
            child = self.findChild(QtCore.QObject, name)
            if child is not None:
                setattr(self, name, child)
            else:
                print("Child '{}' not found!".format(name))

    def setupComboBox(self):
        self.deviceComboBox.addItem('Select a device...')
        self.deviceComboBox.insertSeparator(1)
        self.deviceComboBox.addItem('Refresh list')
        self.deviceComboBox.insertSeparator(3)

        self.deviceComboBox.currentIndexChanged.connect(self.comboBoxCallback)
        self.comboBoxCallback(2)

    def comboBoxCallback(self, newIndex):
        if newIndex == 0:
            pass
        elif newIndex == 2:
            self.refreshDeviceList()
            self.deviceComboBox.setCurrentIndex(0)
        elif newIndex >= 4:
            self.selectDevice(newIndex - 4)

    def clearDevices(self):
        self.propertyViewer.clearContents()
        self.propertyViewer.setRowCount(0)
        MyU3.close_all()
        for i in range(self.deviceComboBox.count(), 3, -1):
            self.deviceComboBox.removeItem(i)

    def refreshDeviceList(self):
        self.clearDevices()
        devices = listAll(self.deviceType)
        self.deviceList = []
        for key in devices.keys():
            self.deviceComboBox.addItem(devices[key]['deviceName'])
            self.deviceList.append(devices[key])

    def selectDevice(self, index):
        dev = self.deviceList[index]
        sn = dev['serialNumber']

        self.myu3instance = MyU3(False, sn)
        self.displayProperties()

    def displayProperties(self):
        self.propertyViewer.setRowCount(len(self.myu3instance.properties))
        for i, (key, val) in enumerate(self.myu3instance.properties.items()):
            self.propertyViewer.setItem(i, 0, QtWidgets.QTableWidgetItem(key))
            self.propertyViewer.setItem(i, 1, QtWidgets.QTableWidgetItem(str(val)))

        self.deviceOpened.emit(self.myu3instance)

    def groupButtons(self, buttons, tag):
        if not hasattr(self, 'buttonGroups'):
            self.buttonGroups = {}

        group = QtWidgets.QButtonGroup()
        for i, b in enumerate(buttons):
            b.setCheckable(True)
            b.setChecked(i == 0)
            group.addButton(b)
            group.setId(b, i)
        group.setExclusive(True)
        self.buttonGroups[tag] = group

    def connectButtons(self):
        pass

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    panel = ConnectPanel()
    panel.show()
    app.exec_()



import sys
import os
import re
import subprocess
from time import time
from math import floor

from PyQt5 import QtCore, QtWidgets, uic, QtGui

from LabjackIO import LabjackIO
from ConnectPanel import ConnectPanel
from labjack import MyU3

starttime = time()

class LabjackApp(QtWidgets.QMainWindow):

    def __init__(self, parent):
        QtWidgets.QDialog.__init__(self)

        self.parent = parent
        # get ui
        self.setWindowTitle('Labjack Python')

        self.mainLayout()

        self.addIOs()

        self.pollInterval = 500 # ms
        self.setupTimer()

        self.connectSignals()

        screenFrac = [0.8, 0.8]
        self.resizeWindow(screenFrac)

        self.instance = None

        self.start()

    def start(self):

        # when everything is ready
        self.show()
        self.raise_()
        return

    def resizeWindow(self, screenFraction):
        desktop = self.parent.desktop()
        geom = self.geometry()
        geom.setWidth(int(screenFraction[0] * desktop.geometry().width()))
        geom.setHeight(int(screenFraction[1] * desktop.geometry().height()))
        geom.moveCenter(desktop.geometry().center())
        self.setGeometry(geom)

    def mainLayout(self):
        self.setCentralWidget(QtWidgets.QWidget())

        hl = QtWidgets.QHBoxLayout()
        self.connectPanel = ConnectPanel()
        self.mainTab = QtWidgets.QTabWidget()
        self.page1 = QtWidgets.QWidget()
        self.mainTab.insertTab(0, self.page1, 'Test Panel')
        self.page1.setEnabled(False)

        hl.addWidget(self.connectPanel)
        hl.addWidget(self.mainTab)
        self.centralWidget().setLayout(hl)

    def addIOs(self):
        self.controlGrid = QtWidgets.QGridLayout()
        Nrows = 8
        channels = MyU3.channelList()

        self.IOs = []
        for i, ch in enumerate(channels):
            row = i % Nrows
            col = floor(i / Nrows)

            f = QtWidgets.QFrame()
            f.setFrameShape(QtWidgets.QFrame.Panel)
            f.setFrameShadow(QtWidgets.QFrame.Raised)
            hl = QtWidgets.QHBoxLayout()
            hl.setContentsMargins(5, 0, 0, 0)
            hl.setSpacing(0)
            l = QtWidgets.QLabel(ch[0])
            l.setAlignment(QtCore.Qt.AlignCenter)
            hl.addWidget(l)
            io = LabjackIO(exclusiveType=ch[1], ioNumber=i)
            self.IOs.append(io)
            hl.addWidget(io)
            f.setLayout(hl)
            self.controlGrid.addWidget(f, row, col)           

        self.page1.setLayout(self.controlGrid)

    def connectSignals(self):
        self.connectPanel.deviceOpened.connect(self.openFunction)
        self.connectPanel.deviceDisconnected.connect(self.disconnectFunction)

    def setupTimer(self):
        self.pollTimer = QtCore.QTimer()
        self.pollTimer.setInterval(self.pollInterval)

    def setupThreading(self):
        if not hasattr(self, 'bkgThread'):
            self.bkgThread = QtCore.QThread()
        else:
            self.bkgThread.quit()

        self.inputsWorker = InputQuerier(self.instance)
        self.inputsWorker.moveToThread(self.bkgThread)
        self.inputsWorker.inputsReady.connect(self.inputHandler)
        self.bkgThread.started.connect(self.inputsWorker.work)

    def checkInstance(self):
        if self.instance == None:
            raise(Exception('No device instance open.'))

    def connectIOcallbacks(self):
        for i, io in enumerate(self.IOs):
            io.typeChanged.connect(self.typeSetFcn)
            io.directionChanged.connect(self.dirSetFcn)
            io.outputStateChanged.connect(self.outputStateSetFcn)

    def removeIOcallbacks(self):
        for i, io in enumerate(self.IOs):
            io.typeChanged.disconnect()
            io.directionChanged.disconnect()
            io.outputStateChanged.disconnect()

    def typeSetFcn(self, ionum, state):
        self.checkInstance()
        self.pollTimer.stop()
        self.instance.setChannelType(ionum, state)
        self.restartTimer()
        self.connectPanel.updatePropertyViewer()

    def dirSetFcn(self, ionum, state):
        self.checkInstance()
        self.pollTimer.stop()
        self.instance.setChannelDir(ionum, state)
        self.restartTimer()
        self.connectPanel.updatePropertyViewer()

    def outputStateSetFcn(self, ionum, state):
        self.checkInstance()
        self.pollTimer.stop()
        self.instance.setChannelOutputState(ionum, state)
        self.restartTimer()
        self.connectPanel.updatePropertyViewer()

    def openFunction(self, instance):
        self.instance = instance
        self.page1.setEnabled(True)
        self.updateChannels()
        self.connectIOcallbacks()

        self.restartTimer()

    def restartTimer(self):
        self.checkInstance()

        self.setupThreading()
        # self.inputs = self.instance.allInputs()
        # self.states = self.instance.getIOstates()
        # # self.pollTimer.timeout.disconnect()
        self.pollTimer.timeout.connect(self.pollFunction)
        self.pollTimer.start()

    def pollFunction(self):
        self.instance.toggleLED()
        self.bkgThread.start()

        # for i in self.instance.allInputs():
        #     # print('{0} isAnalog: {1}'.format(i, self.states[i][0]))
        #     if self.states[i][0]: # this means analog
        #         val = self.instance.getAIN(i)
        #         self.IOs[i].analogReadout.display(val)
        #     else:
        #         val = bool(self.instance.getDIState(i))
        #         self.IOs[i].led.state = val
        # print('Elapsed: {}'.format(time() - starttime))

    @QtCore.pyqtSlot(dict)
    def inputHandler(self, inputs: dict):
        self.bkgThread.quit()

        for key, val in inputs.items():
            if isinstance(val, bool):
                self.IOs[key].inputStateChanged(val)
            else:
                self.IOs[key].analogInputChanged(val)

    def updateChannels(self):
        self.checkInstance()

        self.states = self.instance.getIOstates()
        for (io, state) in zip(self.IOs, self.states):
            isAnalog, isOutput, isHigh = state
            if isAnalog:
                io.analogButton.click()
            else:
                io.digitalButton.click()

            if isOutput:
                io.outputButton.click()
                io.outputSwitch.setCheckState(isHigh)
            else:
                io.inputButton.click()
                io.inputStateChanged(isHigh)

    def disconnectFunction(self):
        self.instance = None
        self.page1.setEnabled(False)
        self.removeIOcallbacks()

class InputQuerier(QtCore.QObject):

    inputsReady = QtCore.pyqtSignal(dict)

    def __init__(self, myu3instance):
        QtCore.QObject.__init__(self)
        self.myu3instance = myu3instance

    @QtCore.pyqtSlot()
    def work(self):

        dataDict = {}

        states = self.myu3instance.getIOstates()
        for i in self.myu3instance.allInputs():
            # print('{0}, isAnalog: {1}, isOutput: {2}'.format(i, states[i][0], states[i][1]))
            if states[i][0]: # this means analog
                val = self.myu3instance.getAIN(i)
            else:
                val = bool(self.myu3instance.getDIState(i))
            dataDict[i] = val

        self.inputsReady.emit(dataDict)



app = QtWidgets.QApplication(sys.argv)
lj = LabjackApp(app)

if __name__ == '__main__':
    sys.exit(app.exec_())
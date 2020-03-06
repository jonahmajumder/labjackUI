# This Python file uses the following encoding: utf-8
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget

class LabjackIO(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.loadIcons()

        self.makeTypeSelectors()
        self.makeReadout()

        self.hl = QtWidgets.QHBoxLayout()

        self.hl.addLayout(self.typeSelector)
        self.hl.addLayout(self.readout)
        self.setLayout(self.hl)

    def loadIcons(self):
        self.icons = {}
        self.icons['analog'] = QtGui.QIcon('icons/analog.svg')
        self.icons['digital'] = QtGui.QIcon('icons/digital.svg')
        self.icons['input'] = QtGui.QIcon('icons/input.svg')
        self.icons['output'] = QtGui.QIcon('icons/output.svg')

    def makeTypeSelectors(self):
        svgsize = QtCore.QSize(40,20)
        buttonsize = QtCore.QSize(65, 40)

        self.typeSelector = QtWidgets.QVBoxLayout()

        self.toDigital = QtWidgets.QPushButton()
        self.toDigital.setIcon(self.icons['digital'])
        self.toDigital.setIconSize(svgsize)
        self.toDigital.setFixedSize(buttonsize)

        self.toAnalog = QtWidgets.QPushButton()
        self.toAnalog.setIcon(self.icons['analog'])
        self.toAnalog.setIconSize(svgsize)
        self.toAnalog.setFixedSize(buttonsize)   

        self.typeSelector.addWidget(self.toDigital)
        self.typeSelector.addWidget(self.toAnalog)

    def makeReadout(self):
        svgsize = QtCore.QSize(40,20)
        buttonsize = QtCore.QSize(65, 40)

        self.readout = QtWidgets.QHBoxLayout()

        self.inputButton = QtWidgets.QPushButton()
        self.inputButton.setIcon(self.icons['input'])
        self.inputButton.setIconSize(svgsize)
        self.inputButton.setFixedSize(buttonsize)   

        self.readoutled = QLED('green')
        self.readout.addWidget(self.inputButton)
        self.readout.addWidget(self.readoutled)


class QLED(QWidget):
    def __init__(self, rgbcolor=''):
        QWidget.__init__(self)

        self.state = True

        colors = ['red', 'green', 'blue']
        try:
            self.colorIdx = colors.index(rgbcolor)
        except ValueError:
            self.colorIdx = 1
            print('Color defaulting to green.')

        self.setMinimumSize(QtCore.QSize(50, 50))

    def dim(self):
        return min(self.geometry().width(), self.geometry().height())

    def centerPoint(self):
        return QtCore.QPoint(round(self.geometry().width()/2), round(self.geometry().height()/2))

    def bkgUpperLeft(self):
        return self.centerPoint() - QtCore.QPoint(round(self.dim()/2), round(self.dim()/2))

    def borderRect(self):
        return QtCore.QRect(self.bkgUpperLeft(), QtCore.QSize(self.dim(), self.dim()))

    def ledRect(self, ledFrac=0.8):
        return self.borderRect().marginsRemoved(QtCore.QMargins() + self.dim()*(1-ledFrac)/2)

    def bkgBrush(self):
        ctr = self.bkgUpperLeft() + 0.9*QtCore.QPoint(self.dim(), self.dim())
        bkggrad = QtGui.QRadialGradient(ctr, self.dim())
        bkggrad.setColorAt(0, Qt.white)
        bkggrad.setColorAt(1, Qt.lightGray)
        return QtGui.QBrush(bkggrad)

    def ledBrush(self):
        ctr = self.bkgUpperLeft() + 0.35*QtCore.QPoint(self.dim(), self.dim())
        addOn = self.state * 150

        middleColor = [0,0,0]
        middleColor[self.colorIdx] = 100+addOn
        outerColor = [0,0,0]
        outerColor[self.colorIdx] = 50+addOn

        ledgrad = QtGui.QRadialGradient(ctr, 0.6*self.dim())
        ledgrad.setColorAt(0, QtGui.QColor(150+addOn, 150+addOn, 150+addOn))
        ledgrad.setColorAt(0.5, QtGui.QColor(*middleColor))
        ledgrad.setColorAt(1, QtGui.QColor(*outerColor))
        return QtGui.QBrush(ledgrad)

    def paintEvent(self, e):
        painter = QtGui.QPainter(self)

        painter.setPen(Qt.NoPen)
        painter.setBrush(self.bkgBrush())
        painter.drawEllipse(self.borderRect())
        painter.setBrush(self.ledBrush())
        painter.drawEllipse(self.ledRect())
        painter.end()

    @property
    def state(self):
        return self.__state

    @state.setter
    def state(self, state):
        self.__state = state
        self.update()

    def toggle(self):
        self.state = not self.state

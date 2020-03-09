# ljwidgets
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget

class QLED(QWidget):
    FILLFRAC = 0.9

    def __init__(self, *args, **kwargs):
        args = list(args)
        rgbcolor = args.pop(0)
        args = tuple(args)

        QWidget.__init__(self, *args, **kwargs)

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
        pixelMargin = self.dim()*(1-self.FILLFRAC)/2
        fullRect = QtCore.QRect(self.bkgUpperLeft(), QtCore.QSize(self.dim(), self.dim()))
        return fullRect.marginsRemoved(QtCore.QMargins() + pixelMargin)

    def ledRect(self, ledFrac=0.8):
        pixelMargin = self.dim()*(1-ledFrac)/2
        return self.borderRect().marginsRemoved(QtCore.QMargins() + pixelMargin)

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

class QGreenLED(QLED):
    COLOR = 'green'
    def __init__(self):
        QLED.__init__(self, self.COLOR)

class QRedLED(QLED):
    COLOR = 'red'
    def __init__(self):
        QLED.__init__(self, self.COLOR)

class QBlueLED(QLED):
    COLOR = 'blue'
    def __init__(self):
        QLED.__init__(self, self.COLOR)





























from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget
from PyQt5 import uic

Form, Base = uic.loadUiType('channel.ui')

class LabjackIO(Base, Form):
    childNames = ['outerGroupBox',
        'typeGroupBox', 'analogButton', 'digitalButton', 'typeStack',
        'analogGroupBox', 'analogLabel', 'analogReadout',
        'directionGroupBox', 'inputButton', 'outputButton', 'directionStack',
        'inputGroupBox', 'inputLabelWidget', 'inputHighLabel', 'inputLowLabel', 'led',
        'outputSwitch']
    ONSS = 'color: rgb(0, 0, 0);'
    OFFSS = 'color: rgba(0, 0, 0, 63);'

    typeChanged = QtCore.pyqtSignal(bool)
    directionChanged = QtCore.pyqtSignal(bool)
    outputStateChanged = QtCore.pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        # self.groupButtons()

        self.setupUi(self)
        self.gatherChildren()

        self.addIcons()

        self.groupButtons((self.analogButton, self.digitalButton), 'type')
        self.groupButtons((self.inputButton, self.outputButton), 'direction')

        self.connectButtons()

        self.setStyleSheet(open('button.css').read())

        # m = self.typeStack.contentsMargins()
        # print(m.left(), m.top(), m.right(), m.bottom())

    def gatherChildren(self):
        for name in self.childNames:
            child = self.findChild(QtCore.QObject, name)
            if child is not None:
                setattr(self, name, child)
            else:
                print("Child '{}' not found!".format(name))

    def addIcons(self):
        typeIconHgt = 20
        dirIconHgt = 16

        self.setButtonIcon(self.analogButton, 'icons/analog.svg', (2*typeIconHgt, typeIconHgt))
        self.setButtonIcon(self.digitalButton, 'icons/digital.svg', (2*typeIconHgt, typeIconHgt))
        self.setButtonIcon(self.inputButton, 'icons/input.svg', (1.5*dirIconHgt, dirIconHgt))
        self.setButtonIcon(self.outputButton, 'icons/output.svg', (1.5*dirIconHgt, dirIconHgt))

    def setButtonIcon(self, button, imagefile, size):
        margins = QtCore.QMargins(5, 10, 5, 10)

        p = QtGui.QPixmap(imagefile)
        ic = QtGui.QIcon(p)
        button.setIcon(ic)
        button.setIconSize(QtCore.QSize(*size))
        button.setFixedSize(QtCore.QSize(*size).grownBy(margins))

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
        for button in self.buttonGroups['type'].buttons():
            button.clicked.connect(self.doTypeChanged)
        self.doTypeChanged()

        for button in self.buttonGroups['direction'].buttons():
            button.clicked.connect(self.doDirectionChanged)
        self.doDirectionChanged()

        self.outputSwitch.stateChanged.connect(self.doOutputStateChanged)
        self.doOutputStateChanged()

    def doTypeChanged(self):
        i = self.buttonGroups['type'].checkedId()
        self.typeStack.setCurrentIndex(i)
        self.typeChanged.emit(i == 0)

    def doDirectionChanged(self):
        i = self.buttonGroups['direction'].checkedId()
        self.directionStack.setCurrentIndex(i)
        self.directionChanged.emit(i == 0)

    def doOutputStateChanged(self):
        newState = self.outputSwitch.isChecked()
        self.directionChanged.emit(newState)

    @QtCore.pyqtSlot(bool)
    def inputStateChanged(self, newState):
        self.led.state = newState
        if newState:
            self.inputHighLabel.setStyleSheet(self.ONSS)
            self.inputLowLabel.setStyleSheet(self.OFFSS)
        else:
            self.inputHighLabel.setStyleSheet(self.OFFSS)
            self.inputLowLabel.setStyleSheet(self.ONSS)

    @QtCore.pyqtSlot(float)
    def analogInputChanged(self, newValue):
        self.analogReadout.display(newValue)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    w = LabjackIO()
    w.show()
    app.exec_()



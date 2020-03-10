import sys
import os
import re
import subprocess
from time import time

from PyQt5 import QtCore, QtWidgets, uic, QtGui

from LabjackIO import LabjackIO

class LabjackApp(QtWidgets.QMainWindow):

    def __init__(self, parent):
        QtWidgets.QDialog.__init__(self)

        self.parent = parent
        # get ui
        self.ui = uic.loadUi('mainwindow.ui')
        self.ui.setWindowTitle('Labjack Python')

        self.addIOs()

        self.start()

    def start(self):

        # when everything is ready
        self.ui.show()
        self.ui.raise_()
        return

    def addIOs(self):

        for col in range(4):
            for row in range(8):
                f = QtWidgets.QFrame()
                f.setFrameShape(QtWidgets.QFrame.Panel)
                f.setFrameShadow(QtWidgets.QFrame.Raised)
                hl = QtWidgets.QHBoxLayout()
                hl.setContentsMargins(0, 0, 0, 0)
                hl.setSpacing(0)
                l = QtWidgets.QLabel('NAME')
                l.setAlignment(QtCore.Qt.AlignCenter)
                hl.addWidget(l)
                hl.addWidget(LabjackIO())
                f.setLayout(hl)
                self.ui.grid.addWidget(f, row, col)

        self.ui.grid.setContentsMargins(0, 0, 0, 0)


app = QtWidgets.QApplication(sys.argv)
lj = LabjackApp(app)

if __name__ == '__main__':
    sys.exit(app.exec_())
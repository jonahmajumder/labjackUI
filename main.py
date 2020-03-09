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
                self.ui.grid.addWidget(LabjackIO(), row, col)


app = QtWidgets.QApplication(sys.argv)
lj = LabjackApp(app)

if __name__ == '__main__':
    sys.exit(app.exec_())
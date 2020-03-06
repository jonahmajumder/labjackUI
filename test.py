from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer

from LabjackIO import LabjackIO

def printmethods(item):
	[print(m) for m in dir(item) if not m.startswith('_')]

app = QApplication([])
w = LabjackIO()
w.show()

if __name__ == '__main__':
	app.exec_()

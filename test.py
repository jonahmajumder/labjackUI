from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer
from PyQt5 import uic

from ConnectPanel import ConnectPanel

from qswitch import QSwitch

def printmethods(item):
	[print(m) for m in dir(item) if not m.startswith('_')]

app = QApplication([])
window = QMainWindow()
# w = QWidget()
# vb = QVBoxLayout()

p = ConnectPanel()
# l2 = LabjackIO()
# vb.addWidget(l1)
# vb.addWidget(l2)
# s = QSwitch()
# vb.addWidget(s)

# w.setLayout(vb)
window.setCentralWidget(p)


window.show()

if __name__ == '__main__':
	app.exec_()

# qswitch
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QCheckBox

class QSwitch(QCheckBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        # self.setMinimumSize(QtCore.QSize(30, 30))
        
        self.clicked.connect(self.click)

        self.vertical = True

        self.marginPx = 2

        self.frac = float(self.isChecked())
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.timerFcn)

    @staticmethod
    def uniformMargins(m):
        return QtCore.QMargins(m, m, m, m)

    def margins(self):
        return self.uniformMargins(self.marginPx)

    def centerPoint(self):
        return QtCore.QPoint(round(self.geometry().width()/2), round(self.geometry().height()/2))

    def contentRect(self):
        rect = self.geometry().marginsRemoved(self.margins())
        rect.moveCenter(self.centerPoint())
        return rect

    @staticmethod
    def distance(qpoint1, qpoint2):
        dp = QtCore.QPoint.dotProduct(qpoint2 - qpoint1, qpoint2 - qpoint1)
        return dp**0.5

    def hitButton(self, qpoint):
        ctrs = self.cocenters()
        distances = [self.distance(qpoint, pt) for pt in ctrs]
        return min(*distances) < float(self.outerRadius())

    def dims(self):
        width, height = self.contentRect().width(), self.contentRect().height()
        # print(width, height)
        if self.vertical:
            mindim = int(min(width, height/2))
            dims = (mindim, 2*mindim)
        else:
            mindim = int(min(width/2, height))
            dims = (2*mindim, mindim)
        # print(dims)
        return dims

    def outerRect(self):
        rect = QtCore.QRect(0, 0, *self.dims())
        rect.moveCenter(self.centerPoint())
        return rect

    def cocenters(self):
        c = self.outerRect().center()
        r = self.outerRadius()
        if self.vertical:
            return (c + QtCore.QPoint(0, r), c - QtCore.QPoint(0, r))
        else:
            return (c - QtCore.QPoint(r, 0), c + QtCore.QPoint(r, 0))

    def outerRadius(self):
        return int(min(self.dims())/2)

    def buttonPos(self):
        # frac = float(self.isChecked())
        ctrs = self.cocenters()
        pos = ctrs[0] + self.frac * (ctrs[1] - ctrs[0])
        return pos

    def buttonRect(self):
        pad = self.outerRadius()/2
        buttonRad = int(2*self.outerRadius()-pad)
        rect = QtCore.QRect(0, 0, buttonRad, buttonRad)
        rect.moveCenter(self.buttonPos())
        return rect

    def textRect(self):
        idx = int(self.isChecked())
        c = self.cocenters()[1 - idx]
        rect = QtCore.QRect(0, 0, 2*self.outerRadius(), 2*self.outerRadius())
        rect.moveCenter(c)
        return rect

    def paintEvent(self, event):
        # super().paintEvent(event)
        # center = self.rect().center()
        # print(self.dims())

        bkgColor = QtGui.QColor(0, 150, 200) if self.isChecked() else QtGui.QColor(200, 200, 200)
        buttonColor = QtGui.QColor(230, 230, 230)
        text = 'I' if self.isChecked() else 'O'
        textColor = QtGui.QColor(230, 230, 230) if self.isChecked() else QtGui.QColor(100, 100, 100)

        painter = QtGui.QPainter(self)
        painter.setBrush(bkgColor)

        penWidth = int(self.outerRadius()/8)

        pen = QtGui.QPen(Qt.white)
        pen.setWidth(penWidth)
        # painter.setPen(pen)
        painter.setPen(Qt.NoPen)

        rect = self.outerRect()
        radius = self.outerRadius()
        painter.drawRoundedRect(rect, radius, radius)

        painter.setBrush(buttonColor)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(self.buttonRect())

        # painter.setBrush(Qt.NoBrush)
        # painter.setPen(pen)
        # painter.drawRoundedRect(rect, radius, radius)

        fnt = painter.font()
        fnt.setPointSize(int(self.outerRadius()))
        fnt.setBold(True)
        painter.setFont(fnt)
        painter.setPen(textColor)
        painter.drawText(self.textRect(), Qt.AlignCenter, text)

        painter.end()

    def click(self):
        self.setupTimer()
        self.timer.start(10)

    def setupTimer(self):
        self.Nsteps = 10
        self.stepNumber = 0
        self.start = self.frac
        self.stop = 1.0 - self.frac
        self.step = (self.stop - self.start)/float(self.Nsteps)

    def timerFcn(self):
        self.frac += self.step
        self.update()
        self.stepNumber += 1
        if self.stepNumber >= self.Nsteps:
            self.timer.stop()


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = QtWidgets.QMainWindow()
    s = QSwitch()
    window.setCentralWidget(s)
    window.show()
    app.exec_()

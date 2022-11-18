import sys, os

from PyQt5 import QtCore, QtWidgets, QtSerialPort, QtGui
from PyQt5.QtSerialPort import QSerialPortInfo
from datetime import datetime

class Widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(Widget, self).__init__(parent)
        self.resize(338,206)
        self.setWindowTitle("Tee\'s Standing Desk Controller")

        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(QtCore.QRect(20, 110, 61, 16))
        self.label.setText("Sit Position")

        self.label_2 = QtWidgets.QLabel(self)
        self.label_2.setGeometry(QtCore.QRect(20, 140, 71, 16))
        self.label_2.setText("Stand Position")

        self.saveButton = QtWidgets.QPushButton(self)
        self.saveButton.setGeometry(QtCore.QRect(180, 140, 75, 23))
        self.saveButton.setText("Save")
        self.saveButton.clicked.connect(self.saveSettings)

        self.loadButton = QtWidgets.QPushButton(self)
        self.loadButton.setGeometry(QtCore.QRect(180, 110, 75, 23))
        self.loadButton.setText("Load")
        self.loadButton.clicked.connect(self.loadSavedFile)

        self.doubleSpinBox = QtWidgets.QDoubleSpinBox(self)
        self.doubleSpinBox.setGeometry(QtCore.QRect(120, 80, 62, 22))


        self.upButton = QtWidgets.QPushButton(self)
        self.upButton.setGeometry(QtCore.QRect(20, 80, 41, 23))
        self.upButton.setText("Up")
        self.upButton.clicked.connect(self.up)

        self.downButton = QtWidgets.QPushButton(self)
        self.downButton.setGeometry(QtCore.QRect(70, 80, 41, 23))
        self.downButton.setText("Down")
        self.downButton.clicked.connect(self.down)

        self.sitButton = QtWidgets.QPushButton(self)
        self.sitButton.setGeometry(QtCore.QRect(200, 60, 51, 31))
        self.sitButton.setText("Sit")
        self.sitButton.clicked.connect(self.sit)

        self.standButton = QtWidgets.QPushButton(self)
        self.standButton.setGeometry(QtCore.QRect(260, 60, 51, 31))
        self.standButton.setText("Stand")
        self.standButton.clicked.connect(self.stand)

        self.statusLabel = QtWidgets.QLabel(self)
        self.statusLabel.setGeometry(QtCore.QRect(210, 10, 111, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.statusLabel.setFont(font)
        self.statusLabel.setText("Not Connected")

        self.sitHeightBox = QtWidgets.QDoubleSpinBox(self)
        self.sitHeightBox.setGeometry(QtCore.QRect(100, 110, 62, 22))

        self.standHeightBox = QtWidgets.QDoubleSpinBox(self)
        self.standHeightBox.setGeometry(QtCore.QRect(100, 140, 62, 22))

        self.stopButton = QtWidgets.QPushButton(self)
        self.stopButton.setGeometry(QtCore.QRect(260, 110, 61, 51))
        self.stopButton.setText("STOP")
        self.stopButton.clicked.connect(self.stopDesk)

        self.heightPosition = QtWidgets.QLabel(self)
        self.heightPosition.setGeometry(QtCore.QRect(30, 10, 61, 31))
        self.heightPosition.setText("0.00")

        font = QtGui.QFont()
        font.setPointSize(14)
        self.heightPosition.setFont(font)
        self.heightPosition.setObjectName("heightPosition")

        self.inchesLable = QtWidgets.QLabel(self)
        self.inchesLable.setGeometry(QtCore.QRect(100, 10, 71, 31))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.inchesLable.setFont(font)
        self.inchesLable.setText("Inches")

        self.comboBox = QtWidgets.QComboBox(self)
        self.comboBox.setGeometry(QtCore.QRect(20, 50, 69, 22))
        self.comboBox.addItems([port.portName() for port in QSerialPortInfo.availablePorts()])

        self.connectButton = QtWidgets.QPushButton(self)
        self.connectButton.setGeometry(QtCore.QRect(110, 50, 75, 23))
        self.connectButton.setCheckable(True)
        self.connectButton.toggled.connect(self.on_toggled)
        self.connectButton.setText("Connect")

        self.serial = QtSerialPort.QSerialPort(
            self.comboBox.currentText(),
            baudRate=QtSerialPort.QSerialPort.Baud115200,
            readyRead=self.receive
        )

        self.timerCheck = QtCore.QTimer()
        self.timerCheck.timeout.connect(self.checkHeight)
        self.timerCheck.start(10000)

    @QtCore.pyqtSlot()
    def receive(self):
        while self.serial.canReadLine():
            data = self.serial.readLine().data().decode()
            data = data.rstrip('\r\n')
            self.processData(data)
            print(data)

    @QtCore.pyqtSlot()
    def send(self, message):
        self.serial.write(message)

    def processData(self, data):
        if data[0] == 'H':
            self.heightPosition.setText(data[1:])
        elif data[0] == 'S':
            self.statusLabel.setText(data[1:])
        else:
            dt = datetime.now()
            with open('debug.txt', 'a') as f:
                f.write("{} - {}".format(data, datetime.timestamp(dt)) + '\n')

    @QtCore.pyqtSlot(bool)
    def on_toggled(self, checked):
        self.connectButton.setText("Disconnect" if checked else "Connect")
        self.statusLabel.setText("Connected")
        if checked:
            if not self.serial.isOpen():
                if not self.serial.open(QtCore.QIODevice.ReadWrite):
                    self.connectButton.setChecked(False)
                    self.statusLabel.setText("Not Connected")
        else:
            self.statusLabel.setText("Not Connected")
            self.serial.close()

    def loadSavedFile(self):
        with open('{}/settings.txt'.format(os.getcwd()), 'r') as f:
            lines = f.readlines()
            sitHeight = lines[0].split(':')[0]
            standHeight = lines[0].split(':')[1]
            self.sitHeightBox.setValue(float(sitHeight))
            self.standHeightBox.setValue(float(standHeight))

    def saveSettings(self):
        with open('{}/settings.txt'.format(os.getcwd()), 'w') as f:
            f.write('{}:{}'.format(self.sitHeightBox.value(), self.standHeightBox.value()))

    def sit(self):
        print("clicked")
        message = '7{}'.format(self.sitHeightBox.value())
        print(message)
        self.send(message.encode())

    def stand(self):
        print("clicked")
        message = '7{}'.format(self.standHeightBox.value())
        print(message)
        self.send(message.encode())

    def stopDesk(self):
        self.send('555'.encode())

    def up(self):
        value = '{}'.format(self.doubleSpinBox.value())
        message = 100.00 + float(value)
        print(message)
        self.send(str(message).encode())

    def down(self):
        value = '{}'.format(self.doubleSpinBox.value())
        message = 200.00 + float(value)
        print(message)
        self.send(str(message).encode())

    def checkHeight(self):
        if not self.serial.isOpen():
            dt = datetime.now()
            with open('debug.txt', 'a') as f:
                f.write("Failed Receiving Desk Height - {}".format(datetime.timestamp(dt)) + '\n')
        else:
            self.send('888'.encode())

def run():
    app = QtWidgets.QApplication(sys.argv)
    w = Widget()
    w.show()
    sys.exit(app.exec_())

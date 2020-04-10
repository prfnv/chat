from PySide2 import QtCore, QtGui, QtWidgets
from interface import Ui_MainWindow

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.message_button.clicked.connect(self.button_handler)

    def button_handler(self):
        self.message_box.appendPlainText(
            self.message_input.text()
        )
        self.message_input.clear()


app = QtWidgets.QApplication() 
window = QtWidgets.QMainWindow()

window.show()
app.exec_()

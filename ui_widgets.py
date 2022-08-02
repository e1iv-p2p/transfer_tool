from PySide2 import QtWidgets, QtGui, QtCore


class Button(QtWidgets.QWidget):
    def __init__(self, label):
        super(Button, self).__init__()
        self.lo = QtWidgets.QHBoxLayout(self)
        self.button = QtWidgets.QPushButton(label)
        self.lo.addWidget(self.button)

    def button_press(self, func):
        self.button.clicked.connect(func)

    def set_text(self, text):
        self.button.setText(text)

    def button_clicked(self):
        pass


class Line(QtWidgets.QWidget):
    def __init__(self, text=None):
        super(Line, self).__init__()
        self.lo = QtWidgets.QHBoxLayout(self)
        if text is None:
            tt = ""
        else:
            tt = text
        self.text = QtWidgets.QLabel(tt)
        self.text.setAlignment(QtCore.Qt.AlignCenter)
        self.lo.addWidget(self.text)

    def set_text(self, text):
        self.text.setText(text)


class Label(QtWidgets.QWidget):
    def __init__(self, label, text=None):
        super(Label, self).__init__()
        self.lo = QtWidgets.QHBoxLayout(self)
        self.label = QtWidgets.QLabel(label)
        self.lo.addWidget(self.label)




























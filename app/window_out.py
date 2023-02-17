from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic


class OUT(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("out.ui", self)
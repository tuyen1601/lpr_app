import cv2
import sys
from datetime import datetime
sys.path.append("../")

from PyQt5.QtWidgets import QMainWindow, QFileDialog
from PyQt5.QtGui import QPixmap
from PyQt5 import uic
from lpr.lprecg import LPRecognizer


class IN(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("in.ui", self)

        self.lprecognizer = LPRecognizer()

        self.btnChooseFile.clicked.connect(self.loadImage)

    def loadImage(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image File", r"/mnt/c/Users/tuyen/Desktop/Project/Do_an/LPR_App/image_test", "Image files (*.jpg *.jpeg *.png)")
        self.labelImage.setScaledContents(True)
        self.labelImage.setPixmap(QPixmap(file_name))

        image = cv2.imread(file_name)
        list_txt, scores = self.lprecognizer.infer(image)
        if scores:
            text = list_txt[scores.index(max(scores))]
        else:
            text = ''
        self.txtLPR.setText(text)
        
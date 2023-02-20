import cv2
import sys
import pytz
import os
from datetime import datetime
sys.path.append("../")

from PyQt5.QtWidgets import QMainWindow, QFileDialog
from PyQt5.QtGui import QPixmap
from PyQt5 import uic

from lpr.lprecg import LPRecognizer

from pymongo import MongoClient
cluster = "mongodb://localhost:27017"
client = MongoClient(cluster)
db = client.lpr
in_collection = db.in_collection

UPLOAD_DIR = "/mnt/c/Users/tuyen/Desktop/Project/Do_an/LPR_App/upload"


def uploadFile(image, file_name):
    if not os.path.exists(UPLOAD_DIR):
        os.mkdir(UPLOAD_DIR)

    timeTerm: str = datetime.now(pytz.timezone('Asia/Ho_Chi_Minh')) \
        .strftime('%Y%m%d%H%M%S')
    imageName: str = f'{timeTerm}-{os.path.basename(file_name)}'
    imagePath: str = os.path.join(UPLOAD_DIR, imageName)
    cv2.imwrite(imagePath, image)

    return imagePath


def send2In(filePath, textLPR):
    dbIn = {"Image Path": filePath, "Licence Plate": textLPR}
    in_collection.insert_one(dbIn)

    return dbIn


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
        filePath = uploadFile(image, file_name)
        list_txt, scores = self.lprecognizer.infer(image)
        if scores:
            text = list_txt[scores.index(max(scores))]
        else:
            text = ''
        self.txtLPR.setText(text)

        dbIn = send2In(filePath, text)
        
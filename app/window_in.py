import cv2
import sys
import pytz
import os
from datetime import datetime
from PIL import ImageQt, Image
sys.path.append("../")

from PyQt5.QtWidgets import QMainWindow, QFileDialog, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5 import uic

from lpr.lprecg import LPRecognizer

from pymongo import MongoClient
cluster = "mongodb://localhost:27017"
client = MongoClient(cluster)
db = client.lpr
in_collection = db.in_collection
manager_collection = db.manager_collection

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


def add2In(idCard, filePath, textLPR, timeIN, status):
    dbIn = {"ID": idCard, "Image Path": filePath, "Licence Plate": textLPR, "Time IN": timeIN, "Status": status}
    in_collection.insert_one(dbIn)

    return dbIn

def messageCheckRegis():
    message = QMessageBox()
    message.setWindowTitle("Message")
    message.setText("Xe Chua Duoc Dang Ky")
    message.setIcon(QMessageBox.Warning)
    message.exec_()

def messageCheckIn():
    message = QMessageBox()
    message.setWindowTitle("Message")
    message.setText("Bien So Khong Hop Le")
    message.setIcon(QMessageBox.Warning)
    message.exec_()


class IN(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("in.ui", self)

        self.lprecognizer = LPRecognizer()

        self.btnChooseFile.clicked.connect(self.vehicleIN)

    def vehicleIN(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image File", r"/mnt/c/Users/tuyen/Desktop/Project/Do_an/LPR_App/image_test", "Image files (*.jpg *.jpeg *.png)")
        idCard = os.path.basename(file_name.split(".")[0])
        self.labelImage.setScaledContents(True)
        self.labelImage.setPixmap(QPixmap(file_name))

        image = cv2.imread(file_name)
        filePath = uploadFile(image, file_name)
        list_txt, scores, plate = self.lprecognizer.infer(image)
        if scores:
            text = list_txt[scores.index(max(scores))]
        else:
            text = ''

        self.labelLP.setScaledContents(True)
        self.labelLP.setPixmap(QPixmap.fromImage(ImageQt.ImageQt(Image.fromarray(plate, mode="RGB"))))

        timeIN = datetime.now().date()
        self.txtLPR.setText(text)

        document = manager_collection.find_one({"ID": idCard})
        if document is None:
            messageCheckRegis()
        else:
            for key, value in document.items():
                if key == "Licence Plate":
                    if value == text:
                        status = "In"
                        dbIn = add2In(idCard ,filePath, text, str(timeIN), status)
                    else:
                        messageCheckIn()
                        break

        
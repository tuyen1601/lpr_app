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

def messageCheckIn(trueLP):
    message = QMessageBox()
    message.setWindowTitle("Message")
    # message.setText("Bien So Khong Hop Le")
    message.setText("Bien So Dang Ky: " + trueLP)
    message.setIcon(QMessageBox.Warning)
    message.exec_()


class IN(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("in.ui", self)

        self.lprecognizer = LPRecognizer()

        self.btnChooseFile.clicked.connect(self.vehicleIN)

    def vehicleIN(self):
        #read image 
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Image File", r"/mnt/c/Users/tuyen/Desktop/Project/Do_an/LPR_App/image_test", "Image files (*.jpg *.jpeg *.png)")

        #licence plate recognizer
        image = cv2.imread(fileName)
        list_txt, scores, plate = self.lprecognizer.infer(image)
        if scores:
            text = list_txt[scores.index(max(scores))]
        else:
            text = ''

        #upload image
        _fileName = fileName.split(".")[0] + "_plate." + fileName.split(".")[1]
        filePath = uploadFile(image, fileName)
        _filePath = uploadFile(plate, _fileName)

        #set lane vehicle
        timeIN = datetime.now().date()
        idCard = os.path.basename(fileName.split(".")[0])
        nameVehicle = idCard.split("_")[0]
        if nameVehicle == "car":
            #car image
            self.lblImgCar.setScaledContents(True)
            self.lblImgCar.setPixmap(QPixmap(fileName))
            #plate image
            self.lblPlateCar.setScaledContents(True)
            self.lblPlateCar.setPixmap(QPixmap.fromImage(ImageQt.ImageQt(Image.fromarray(plate, mode="RGB"))))
            #text LP
            self.txtLPCar.setText(text)
        else:
            #motobike image
            self.lblImgMotobike.setScaledContents(True)
            self.lblImgMotobike.setPixmap(QPixmap(fileName))
            #plate image
            self.lblPlateMotobike.setScaledContents(True)
            self.lblPlateMotobike.setPixmap(QPixmap.fromImage(ImageQt.ImageQt(Image.fromarray(plate, mode="RGB"))))
            #text LP
            self.txtLPMotobike.setText(text)

        document = manager_collection.find_one({"ID": idCard})
        self.lw.clear()
        if document is None:
            messageCheckRegis()
        else:
            for key, value in document.items():
                if key == "Licence Plate":
                    if value == text:
                        status = "In"
                        dbIn = add2In(idCard ,filePath, text, str(timeIN), status)
                    else:
                        messageCheckIn(value)
                        break
            self.lw.addItem("ID: " + idCard)
            self.lw.addItem("Time IN: " + str(timeIN))

        
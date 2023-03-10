import cv2
import sys
import os
from datetime import datetime
from PIL import ImageQt, Image
sys.path.append("../")

from PyQt5.QtWidgets import QMainWindow, QFileDialog, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5 import uic

from lpr.lprecg import LPRecognizer

from pymongo import MongoClient
cluster = "mongodb://10.37.239.135:27017"
client = MongoClient(cluster)
db = client.lpr
in_collection = db.in_collection
manager_collection = db.manager_collection

UPLOAD_DIR = "/mnt/c/Users/tuyen/Desktop/Project/Do_an/LPR_App/upload"


def uploadFile(image, file_name):
    if not os.path.exists(UPLOAD_DIR):
        os.mkdir(UPLOAD_DIR)

    timeTerm: str = datetime.now().strftime('%Y%m%d%H%M%S')
    imageName: str = f'{timeTerm}-{os.path.basename(file_name)}'
    imagePath: str = os.path.join(UPLOAD_DIR, imageName)
    cv2.imwrite(imagePath, image)

    return imagePath

def add2In(idCard, filePath, cardType, textLPR, timeIN, status):
    dbIn = {"ID": idCard, "Image Path": filePath, "Loại vé": cardType, "Biển số": textLPR, "Thời gian vào": timeIN, "Status": status}
    in_collection.insert_one(dbIn)

    return dbIn

def checkDate(strDateRegis, strDateExpired, timeIN):
    objDateRegis = datetime.strptime(strDateRegis, "%d %m %Y")
    objDateExpired = datetime.strptime(strDateExpired, "%d %m %Y")
    if timeIN >= objDateRegis and timeIN <= objDateExpired:
        return True
    else:
        return False

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

def messageCheckDate():
    message = QMessageBox()
    message.setWindowTitle("Message")
    message.setText("The het han")
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
        if fileName:
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
            nameVehicle = os.path.dirname(fileName).split("/")[-1]

            timeIN = datetime.now()
            strTimeIN = timeIN.strftime('%Hh%Mp - %d/%m/%Y')
            idCard = os.path.basename(fileName.split(".")[0])
            if nameVehicle == "car":
                #car image
                self.lblImgCar.setScaledContents(True)
                self.lblImgCar.setPixmap(QPixmap(fileName))
                #plate image
                self.lblPlateCar.setScaledContents(True)
                # self.lblPlateCar.setPixmap(QPixmap.fromImage(ImageQt.ImageQt(Image.fromarray(plate, mode="RGB"))))
                self.lblPlateCar.setPixmap(QPixmap(_filePath))
                #text LP
                self.txtLPCar.setText(text)
            else:
                #motobike image
                self.lblImgMotobike.setScaledContents(True)
                self.lblImgMotobike.setPixmap(QPixmap(fileName))
                #plate image
                self.lblPlateMotobike.setScaledContents(True)
                # self.lblPlateMotobike.setPixmap(QPixmap.fromImage(ImageQt.ImageQt(Image.fromarray(plate, mode="RGB"))))
                self.lblPlateMotobike.setPixmap(QPixmap(_filePath))
                #text LP
                self.txtLPMotobike.setText(text)

            document = manager_collection.find_one({"ID": idCard})
            self.lw.clear()
            if document is None:
                messageCheckRegis()
            else:
                valuesList = list(document.values())
                if not checkDate(valuesList[5], valuesList[6], timeIN):
                    messageCheckDate()
                self.lw.addItem("ID: " + idCard)
                self.lw.addItem("Thời gian vào: " + strTimeIN)
                if len(valuesList) > 3:
                    self.lw.addItem("Loại vé: " + valuesList[4])
                    if valuesList[2] == text:
                        status = "In"
                        # dbIn = add2In(idCard, filePath, valuesList[4], text, timeIN, status)
                    else:
                        messageCheckIn()
                else:
                    self.lw.addItem("Loại vé: " + valuesList[2])
                    status = "In"
                    # dbIn = add2In(idCard, filePath, valuesList[2], text, timeIN, status)

import cv2
import sys
import os
from datetime import datetime
from PIL import ImageQt, Image
sys.path.append("../")

from lpr.lprecg import LPRecognizer

from PyQt5.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QListWidget
from PyQt5.QtGui import QPixmap
from PyQt5 import uic

from pymongo import MongoClient
cluster = "mongodb://localhost:27017"
client = MongoClient(cluster)
db = client.lpr
in_collection = db.in_collection
manager_collection = db.manager_collection
out_collection = db.out_collection

def add2Out(idCard, textLPR, timeOUT, status):
    dbOut = {"ID": idCard, "Licence Plate": textLPR, "Time OUT": timeOUT, "Status": status}
    out_collection.insert_one(dbOut)

    return dbOut

def messageCheckOut():
    message = QMessageBox()
    message.setWindowTitle("Message")
    message.setText("Bien So Khong Hop Le")
    message.setIcon(QMessageBox.Warning)
    message.exec_()

def messageCheckCard():
    message = QMessageBox()
    message.setWindowTitle("Message")
    message.setText("The Khong Hop Le")
    message.setIcon(QMessageBox.Warning)
    message.exec_()


class OUT(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("out.ui", self)

        self.lprecognizer = LPRecognizer()

        self.btnChooseFile.clicked.connect(self.vehicleOUT)
    
    def vehicleOUT(self):
        #read image
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image File", r"/mnt/c/Users/tuyen/Desktop/Project/Do_an/LPR_App/image_test", "Image files (*.jpg *.jpeg *.png)")
        
        #licence plate recognizer
        image = cv2.imread(file_name)
        list_txt, scores, plate = self.lprecognizer.infer(image)
        if scores:
            text = list_txt[scores.index(max(scores))]
        else:
            text = ''

        #set lane vehicle
        timeOUT = datetime.now().date()
        idCard = os.path.basename(file_name.split(".")[0])
        nameVehicle = idCard.split("_")[0]
        if nameVehicle == "car":
            self.lblImgInCar.clear()
            self.lblPlateInCar.clear()
            #car image out
            self.lblImgOutCar.setScaledContents(True)
            self.lblImgOutCar.setPixmap(QPixmap(file_name))
            #plate image out
            self.lblPlateOutCar.setScaledContents(True)
            self.lblPlateOutCar.setPixmap(QPixmap.fromImage(ImageQt.ImageQt(Image.fromarray(plate, mode="RGB"))))
            #text LP
            self.txtLPCar.setText(text)
        else:
            self.lblImgInMotobike.clear()
            self.lblPlateInMotobike.clear()
            #motobike image out
            self.lblImgOutMotobike.setScaledContents(True)
            self.lblImgOutMotobike.setPixmap(QPixmap(file_name))
            #plate image out
            self.lblPlateOutMotobike.setScaledContents(True)
            self.lblPlateOutMotobike.setPixmap(QPixmap.fromImage(ImageQt.ImageQt(Image.fromarray(plate, mode="RGB"))))
            #text LP
            self.txtLPMotobike.setText(text)

        document = in_collection.find_one({"ID": idCard})
        self.lw.clear()
        if document is None:
            messageCheckCard()
        else:
            for key, value in document.items():
                if key == "Image Path":
                    if nameVehicle == "car":
                        self.lblImgInCar.setScaledContents(True)
                        self.lblImgInCar.setPixmap(QPixmap(value))
                        self.lblPlateInCar.setScaledContents(True)
                        self.lblPlateInCar.setPixmap(QPixmap(value.split(".")[0] + "_plate." + value.split(".")[1]))
                    else:
                        self.lblImgInMotobike.setScaledContents(True)
                        self.lblImgInMotobike.setPixmap(QPixmap(value))
                        self.lblPlateInMotobike.setScaledContents(True)
                        self.lblPlateInMotobike.setPixmap(QPixmap(value.split(".")[0] + "_plate." + value.split(".")[1]))
                if key == "Time IN":
                    self.lw.addItem("ID: " + idCard)
                    self.lw.addItem("Time IN: " + value)
                    self.lw.addItem("Time OUT: " + str(timeOUT))
                if key == "Licence Plate":
                    if value == text:
                        status = "Out"
                        # dbOut = add2Out(idCard, text, str(timeOUT), status)
                    else:
                        messageCheckOut()
                        break

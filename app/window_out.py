import cv2
import sys
import os
from datetime import datetime
from PIL import ImageQt, Image
sys.path.append("../")

from lpr.lprecg import LPRecognizer

from PyQt5.QtWidgets import QMainWindow, QFileDialog, QMessageBox
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
    dbOut = {"ID": idCard, "Licence Plate": textLPR, "Time IN": timeOUT, "Status": status}
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
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image File", r"/mnt/c/Users/tuyen/Desktop/Project/Do_an/LPR_App/image_test", "Image files (*.jpg *.jpeg *.png)")
        idCard = os.path.basename(file_name.split(".")[0])
        self.lblImgOut.setScaledContents(True)
        self.lblImgOut.setPixmap(QPixmap(file_name))

        image = cv2.imread(file_name)
        list_txt, scores, plate = self.lprecognizer.infer(image)
        if scores:
            text = list_txt[scores.index(max(scores))]
        else:
            text = ''

        self.lblPlateOut.setScaledContents(True)
        self.lblPlateOut.setPixmap(QPixmap.fromImage(ImageQt.ImageQt(Image.fromarray(plate, mode="RGB"))))

        timeOUT = datetime.now().date()
        self.txtLPR.setText(text)

        document = in_collection.find_one({"ID": idCard})
        if document is None:
            self.lblImgIn.clear()
            messageCheckCard()
        else:
            for key, value in document.items():
                if key == "Image Path":
                    self.lblImgIn.setScaledContents(True)
                    self.lblImgIn.setPixmap(QPixmap(value))
                if key == "Licence Plate":
                    if value == text:
                        status = "Out"
                        # dbOut = add2Out(idCard, text, str(timeOUT), status)
                    else:
                        messageCheckOut()
                        break


import sys
import os
import glob
import cv2

from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog
from PySide6.QtCore import Qt, QFile, Slot
from PySide6.QtGui import QPixmap, QImage
from src.ui_mainwindow import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.imageLabel.setGeometry(0, 0, 640, 512)  # initial size
        self.current_image = None

        # menu actions
        self.ui.actionOpen_Folder.triggered.connect(self.open_folder)
        self.ui.actionClose_Folder.triggered.connect(self.close_folder)
        self.ui.actionCrop_All.triggered.connect(self.crop_all)
        
        # buttons


        # image selection changed
        self.ui.imagesListWidget.currentItemChanged.connect(self.image_selection_changed)


    def resizeEvent(self, event):
        self.update_image_label()


    def open_folder(self):
        dir = QFileDialog.getExistingDirectory(
            self, caption="Open Dataset", options=QFileDialog.ShowDirsOnly)
        if dir == "":
            return
        self.image_dir = dir
        self.load_image_files()
        self.populate_image_list()


    def close_folder(self):
        print("Closing open folder")
        # TODO: reset everything into intial state


    def crop_all(self):
        print("Cropping annotated rectangles for all images in opened folder")
        pass


    def load_image_files(self):
        self.image_files = []
        for file_type in ["jpg", "JPG", "png", "PNG", "tiff", "TIFF"]:
            files = sorted(glob.glob(os.path.join(self.image_dir, "*.{}".format(file_type))))
            self.image_files.extend(files)
        print(self.image_files)

    
    def populate_image_list(self):
        for image_file in self.image_files:
            file_name = os.path.basename(image_file)
            self.ui.imagesListWidget.addItem(file_name)


    @Slot()
    def image_selection_changed(self): #, current, previous):
        current = self.ui.imagesListWidget.currentItem()
        if not current:
            return
        selected_image_file = current.text()
        print("Image selection changed")
        self.load_selected_image(selected_image_file)


    def load_selected_image(self, selected_image_file):
        image_file = os.path.join(self.image_dir, selected_image_file)
        image = cv2.imread(image_file)
        height, width, _ = image.shape[:3]
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        bytesPerLine = 3 * width
        qt_image = QImage(image.data, width, height, bytesPerLine, QImage.Format_RGB888)
        self.current_image = QPixmap(qt_image)
        self.update_image_label()


    @Slot()
    def update_image_label(self):
        if self.current_image:
            w = self.ui.imageLabel.width()
            h = self.ui.imageLabel.height()
            self.ui.imageLabel.setPixmap(self.current_image.scaled(w, h, Qt.KeepAspectRatio))
            self.ui.imageLabel.mousePressEvent = self.getImagePos

    
    def getImagePos(self, event):
        # get current scale factor
        width_scaled = self.ui.imageLabel.width()
        height_scaled = self.ui.imageLabel.height()
        width_orig = self.current_image.size().width()
        height_orig = self.current_image.size().height()

        width_scale = width_orig / width_scaled
        height_scale = height_orig / height_scaled

        x = width_scale * event.position().x()
        y = height_scale * event.position().y()
        print(x, y)
        #c = self.img.pixel(x,y)  # color code (integer): 3235912
        # depending on what kind of value you like (arbitary examples)
        #c_qobj = QColor(c)  # color object
        #c_rgb = QColor(c).getRgb()  # 8bit RGBA: (255, 23, 0, 255)
        #c_rgbf = QColor(c).getRgbf()  # RGBA float: (1.0, 0.3123, 0.0, 1.0)
        #return x, y, c_rgb

        



if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
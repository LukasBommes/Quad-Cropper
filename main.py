import sys
import os
import glob
import json

import numpy as np
import cv2

from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog
from PySide6.QtCore import Qt, QObject, Slot, Signal, QPointF
from PySide6.QtGui import QPixmap, QImage, QPainter, QColor, QPolygonF
from src.ui_mainwindow import Ui_MainWindow

from src.utils import sort_cw, crop_module


#TODO:
# click "new rectangle"
# click four corner points, on each click draw a point
# once we have four points, draw a rectangle, add rectangale to list of rectangles for this image

# feature: keyboard shortcuts ("N" for new rectangle, "esc" to aboard drawing rectangle, ...)

# feature: delete all existing annotations...


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.imageLabel.setGeometry(0, 0, 640, 512)  # initial size
        self.disable()
        self.model = Model()

        self.model.current_image_changed.connect(self.update_image_label)
        self.model.current_rectangle_changed.connect(self.update_image_label)
        self.model.rectangles_changed.connect(self.rectangles_changed)
        self.model.rectangles_changed.connect(self.update_image_label)
        self.model.image_files_changed.connect(self.update_image_list)

        # menu actions
        self.ui.actionOpen_Folder.triggered.connect(self.open_folder)
        self.ui.actionClose_Folder.triggered.connect(self.close_folder)
        self.ui.actionCrop_All.triggered.connect(self.crop_all)
        
        # buttons
        self.ui.deleteRectangleButton.clicked.connect(self.delete_rectangle_button_clicked)

        # image selection changed
        self.ui.imagesListWidget.currentItemChanged.connect(self.image_selection_changed)


    def enable(self):
        self.ui.actionOpen_Folder.setEnabled(False)
        self.ui.actionClose_Folder.setEnabled(True)
        self.ui.actionCrop_All.setEnabled(True)

    
    def disable(self):
        self.ui.actionOpen_Folder.setEnabled(True)
        self.ui.actionClose_Folder.setEnabled(False)
        self.ui.actionCrop_All.setEnabled(False)


    def resizeEvent(self, event):
        self.update_image_label()


    @Slot()
    def open_folder(self):
        dir = QFileDialog.getExistingDirectory(
            self, caption="Open Dataset", options=QFileDialog.ShowDirsOnly)
        if dir == "":
            return
        self.model.image_dir = dir
        # check if meta.json is available and load into model
        try:
            with open(os.path.join(dir, "meta.json"), "r") as file:
                self.model.rectangles = json.load(file)
        except FileNotFoundError:
            pass
        self.get_image_files()
        self.enable()
        print("Dataset opened")


    @Slot()
    def close_folder(self):
        self.model.reset()
        self.disable()
        print("Dataset closed")


    @Slot()
    def crop_all(self):
        if not self.model.current_image:
            return
        # select output directory
        output_dir = QFileDialog.getExistingDirectory(
            self, caption="Select Output Directory", options=QFileDialog.ShowDirsOnly)
        if output_dir == "":
            return

        # crop and rectify annotated regions from current image
        try:
            image_file = self.model.current_image["filename"]
            rectangles = self.model.rectangles[image_file]
        except KeyError:
            return

        for rectangle_id, rectangle in enumerate(rectangles):
            rectangle = sort_cw(np.array(rectangle))
            rectangle = rectangle.reshape(4, 1, 2)
            image = self.model.current_image["image"]
            image_cropped, _ = crop_module(image, rectangle, crop_width=None, crop_aspect=None, rotate_mode=None)
            cv2.imwrite(os.path.join(output_dir, "{}_{}".format(image_file, rectangle_id)), image_cropped)
        print("Cropped annotated rectangles for all images in opened folder")


    def get_image_files(self):
        image_files = []
        for file_type in ["jpg", "JPG", "png", "PNG", "tiff", "TIFF"]:
            files = sorted(glob.glob(os.path.join(self.model.image_dir, "*.{}".format(file_type))))
            image_files.extend(files)
        self.model.image_files = image_files

    
    def update_image_list(self, image_files):
        self.ui.imagesListWidget.clear()
        for image_file in image_files:
            file_name = os.path.basename(image_file)
            self.ui.imagesListWidget.addItem(file_name)


    @Slot()
    def image_selection_changed(self):
        self.model.current_rectangle = []
        self.model.current_image = None
        # get name of selected image
        current = self.ui.imagesListWidget.currentItem()
        if not current:
            return
        selected_image_file = current.text()
        # load selected image
        image_file = os.path.join(self.model.image_dir, selected_image_file)
        image = cv2.imread(image_file)
        height, width, _ = image.shape[:3]
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        bytesPerLine = 3 * width
        qt_image = QImage(image_rgb.data, width, height, bytesPerLine, QImage.Format_RGB888)
        self.model.current_image = {
            "filename": selected_image_file,
            "pixmap": QPixmap(qt_image),
            "image": image,
        }


    @Slot()
    def update_image_label(self):
        w = self.ui.imageLabel.width()
        h = self.ui.imageLabel.height()

        if not self.model.current_image:
            pixmap = QPixmap("src/no_image.png")
            self.ui.imageLabel.setPixmap(pixmap.scaled(w, h, Qt.KeepAspectRatio))
            return
        
        pixmap = self.model.current_image["pixmap"].copy()

        # draw current rectangle
        painter = QPainter(pixmap)
        painter.setBrush(Qt.red)
        for corner in self.model.current_rectangle:
            painter.drawEllipse(QPointF(*corner), 5, 5)
        painter.end()

        # draw rectangles
        try:
            image_file = self.model.current_image["filename"]
            rectangles = self.model.rectangles[image_file]
        except KeyError:
            pass
        else:
            painter = QPainter(pixmap)
            for rectangle in rectangles:
                polygon = QPolygonF()
                painter.setBrush(QColor(0, 255, 0, 255))
                for corner in sort_cw(np.array(rectangle)):
                    painter.drawEllipse(QPointF(*corner), 5, 5)
                    polygon.append(QPointF(*corner))
                painter.setBrush(QColor(0, 255, 0, 100))
                painter.drawConvexPolygon(polygon)
            painter.end()            

        self.ui.imageLabel.setPixmap(pixmap.scaled(w, h, Qt.KeepAspectRatio))
        self.ui.imageLabel.mousePressEvent = self.getImagePos

    
    def getImagePos(self, event):
        # get current image scale
        width_scaled = self.ui.imageLabel.pixmap().size().width() #self.ui.imageLabel.width()
        height_scaled = self.ui.imageLabel.pixmap().size().height() #self.ui.imageLabel.height()
        width_orig = self.model.current_image["pixmap"].size().width()
        height_orig = self.model.current_image["pixmap"].size().height()
        width_scale = width_orig / width_scaled
        height_scale = height_orig / height_scaled

        x_scaled = event.position().x()
        y_scaled = event.position().y()
        x_orig = width_scale * x_scaled
        y_orig = height_scale * y_scaled
        print(x_scaled, y_scaled, x_orig, y_orig)
        self.add_point_to_current_rectangle(x_orig, y_orig)


    def add_point_to_current_rectangle(self, x, y):
        current_rectangle_copy = self.model.current_rectangle.copy()
        current_rectangle_copy.append((x, y))
        print("self.model.current_rectangle: ", current_rectangle_copy)
        self.model.current_rectangle = current_rectangle_copy
        if len(current_rectangle_copy) < 4:
            return
        self.create_new_rectangle()
        

    def create_new_rectangle(self):
        image_file = self.model.current_image["filename"]
        rectangles_copy = self.model.rectangles.copy()
        try:
            rectangles_copy[image_file].append(
                self.model.current_rectangle
            )
        except KeyError:
            rectangles_copy[image_file] = [
                self.model.current_rectangle
            ]
        self.model.rectangles = rectangles_copy
        self.model.current_rectangle = []
        print("self.model.current_rectangle: ", self.model.current_rectangle)
        print("self.model.rectangles: ", self.model.rectangles)

    
    @Slot()
    def rectangles_changed(self):
        if not self.model.image_dir:
            return
        with open(os.path.join(self.model.image_dir, "meta.json"), "w") as file:
            json.dump(self.model.rectangles, file)
        #self.populate_rectangle_list()


    # TODO: finish this function, highlight selected rectangle
    def populate_rectangle_list(self):
        if not self.model.current_image:
            return
        file_name = self.model.current_image["filename"]
        try:
            rectangle = self.model.rectangles[file_name]
            self.ui.rectanglesListWidget.addItem(file_name)
        except KeyError:
            pass


    @Slot()
    def delete_rectangle_button_clicked(self):
        # TODO: get selected rectangle from list
        # delete rectangle from mode.rectangles
        # redraw
        pass



class Model(QObject):
    rectangles_changed = Signal(object)
    current_rectangle_changed = Signal(object)
    current_image_changed = Signal(object)
    image_files_changed = Signal(list)

    def __init__(self):
        super().__init__()
        self._image_dir = None
        self._image_files = []
        self._rectangles = {}
        self._current_rectangle = []
        self._current_image = None

    def reset(self):
        self.image_dir = None
        self.image_files = []
        self.rectangles = {}
        self.current_rectangle = []
        self.current_image = None


    @property
    def image_dir(self):
        return self._image_dir

    @image_dir.setter
    def image_dir(self, value):
        self._image_dir = value

    @property
    def image_files(self):
        return self._image_files

    @image_files.setter
    def image_files(self, value):
        self._image_files = value
        self.image_files_changed.emit(value)

    @property
    def rectangles(self):
        return self._rectangles

    @rectangles.setter
    def rectangles(self, value):
        self._rectangles = value
        self.rectangles_changed.emit(value)

    @property
    def current_rectangle(self):
        return self._current_rectangle

    @current_rectangle.setter
    def current_rectangle(self, value):
        self._current_rectangle = value
        self.current_rectangle_changed.emit(value)

    @property
    def current_image(self):
        return self._current_image

    @current_image.setter
    def current_image(self, value):
        self._current_image = value
        self.current_image_changed.emit(value)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    screen = window.screen()
    window.resize(screen.availableSize() * 0.5)
    window.show()

    sys.exit(app.exec())
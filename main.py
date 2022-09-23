import sys
import os
import glob
import json
import cv2

from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog
from PySide6.QtCore import Qt, QObject, Slot, Signal, QPointF
from PySide6.QtGui import QPixmap, QImage, QPainter
from src.ui_mainwindow import Ui_MainWindow


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
        self.model = Model()

        self.model.current_image_changed.connect(self.update_image_label)
        self.model.current_rectangle_changed.connect(self.update_image_label)
        self.model.rectangles_changed.connect(self.rectangles_changed)
        self.model.rectangles_changed.connect(self.update_image_label)

        # menu actions
        self.ui.actionOpen_Folder.triggered.connect(self.open_folder)
        self.ui.actionClose_Folder.triggered.connect(self.close_folder)
        self.ui.actionCrop_All.triggered.connect(self.crop_all)
        
        # buttons
        self.ui.newRectangleButton.clicked.connect(self.new_rectangle_button_clicked)
        self.ui.deleteRectangleButton.clicked.connect(self.delete_rectangle_button_clicked)

        # image selection changed
        self.ui.imagesListWidget.currentItemChanged.connect(self.image_selection_changed)


    def reset(self):
        self.model.current_rectangle = []
        self.model.current_image = None


    def resizeEvent(self, event):
        self.update_image_label()


    def open_folder(self):
        dir = QFileDialog.getExistingDirectory(
            self, caption="Open Dataset", options=QFileDialog.ShowDirsOnly)
        if dir == "":
            return
        self.image_dir = dir
        # check if meta.json is available and load into model
        try:
            with open(os.path.join(dir, "meta.json"), "r") as file:
                self.model.rectangles = json.load(file)
        except FileNotFoundError:
            pass
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
    def image_selection_changed(self):
        self.reset()
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
        self.model.current_image = {
            "filename": selected_image_file,
            "pixmap": QPixmap(qt_image)
        }


    @Slot()
    def update_image_label(self):
        if not self.model.current_image:
            return
        w = self.ui.imageLabel.width()
        h = self.ui.imageLabel.height()
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
            painter.setBrush(Qt.red)
            for rectangle in rectangles:
                for corner in rectangle:
                    painter.drawEllipse(QPointF(*corner), 5, 5)
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
        print("rectangles changed")
        with open(os.path.join(self.image_dir, "meta.json"), "w") as file:
            json.dump(self.model.rectangles, file)
        self.populate_rectangle_list()


    # TODO: finish this function, highlight selected rectangle
    def populate_rectangle_list(self):
       file_name = self.current_image["filename"]
       try:
           rectangle = self.model.rectangles[file_name]
           self.ui.rectanglesListWidget.addItem(file_name)
       except KeyError:
           pass
            

    @Slot()
    def new_rectangle_button_clicked(self):
        if not self.model.current_image:
            return
        # now click four corner points (TODO. show helper text in status bar...)
        self.model.current_rectangle = []


    @Slot()
    def delete_rectangle_button_clicked(self):
        # TODO: get selected rectangle from list
        # delete rectangle from mode.rectangles
        # redraw
        pass



class Model(QObject):
    rectangles_changed = Signal()
    current_rectangle_changed = Signal(object)
    current_image_changed = Signal()

    def __init__(self):
        super().__init__()
        self._rectangles = {}
        self._current_rectangle = []
        self._current_image = None

    @property
    def rectangles(self):
        return self._rectangles

    @rectangles.setter
    def rectangles(self, value):
        self._rectangles = value
        self.rectangles_changed.emit()

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
        self.current_image_changed.emit()



if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
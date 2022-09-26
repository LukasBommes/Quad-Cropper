def main():
    import sys
    import os
    import glob
    import json
    import uuid
    from collections import defaultdict

    import numpy as np
    import cv2

    from PySide6 import QtCore, QtGui, QtWidgets
    from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, \
        QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QFrame
    from PySide6.QtCore import Qt, QObject, Slot, Signal, QPoint, QPointF, QRectF
    from PySide6.QtGui import QPixmap, QImage, QPainter, QColor, QPolygonF
    from src.ui_mainwindow import Ui_MainWindow

    from src.utils import sort_cw, crop_module


    class PhotoViewer(QGraphicsView):
        photoClicked = Signal(QPoint)

        def __init__(self, parent):
            super(PhotoViewer, self).__init__(parent)
            self._zoom = 0
            self._empty = True
            self._scene = QGraphicsScene(self)
            self._photo = QGraphicsPixmapItem()
            self._scene.addItem(self._photo)
            self.setScene(self._scene)
            self.setDragMode(QGraphicsView.NoDrag)
            self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
            self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(30, 30, 30)))
            self.setFrameShape(QFrame.NoFrame)

        def hasPhoto(self):
            return not self._empty

        def fitInView(self, scale=True):
            rect = QRectF(self._photo.pixmap().rect())
            if not rect.isNull():
                self.setSceneRect(rect)
                if self.hasPhoto():
                    unity = self.transform().mapRect(QRectF(0, 0, 1, 1))
                    self.scale(1 / unity.width(), 1 / unity.height())
                    viewrect = self.viewport().rect()
                    scenerect = self.transform().mapRect(rect)
                    factor = min(viewrect.width() / scenerect.width(),
                                viewrect.height() / scenerect.height())
                    self.scale(factor, factor)
                self._zoom = 0

        def setPhoto(self, pixmap=None, fit_in_view=True):
            if fit_in_view:
                self._zoom = 0
            if pixmap and not pixmap.isNull():
                self._empty = False
                self._photo.setPixmap(pixmap)
            else:
                self._empty = True
                self._photo.setPixmap(QPixmap())
            if fit_in_view:
                self.fitInView()

        def wheelEvent(self, event):
            if self.hasPhoto():
                if event.angleDelta().y() > 0:
                    factor = 1.25
                    self._zoom += 1
                else:
                    factor = 0.8
                    self._zoom -= 1
                if self._zoom > 0:
                    self.scale(factor, factor)
                elif self._zoom == 0:
                    self.fitInView()
                else:
                    self._zoom = 0

        def mousePressEvent(self, event):
            if self._photo.isUnderMouse():
                self.photoClicked.emit(self.mapToScene(event.pos()).toPoint())
            super(PhotoViewer, self).mousePressEvent(event)



    class MainWindow(QMainWindow):
        def __init__(self):
            super(MainWindow, self).__init__()
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)
            self.setWindowTitle("QuadCropper")
            self.disable()
            self.model = Model()

            # image viewer
            self.viewer = PhotoViewer(self)
            self.viewer.photoClicked.connect(self.photoClicked)        
            self.ui.gridLayout.addWidget(self.viewer, 0, 1, 1, 1)

            self.model.current_image_changed.connect(lambda _: self.update_image_label(fit_in_view=True))
            self.model.current_rectangle_changed.connect(lambda _: self.update_image_label(fit_in_view=False))
            self.model.rectangles_changed.connect(self.save_rectangles)
            self.model.rectangles_changed.connect(lambda _: self.update_image_label(fit_in_view=False))        
            self.model.image_files_changed.connect(self.update_image_list)
            self.model.current_image_changed.connect(self.update_rectangle_list)
            self.model.rectangles_changed.connect(self.update_rectangle_list)
            self.model.selected_rectangle_changed.connect(self.selected_rectangle_changed)
            self.model.selected_rectangle_changed.connect(lambda _: self.update_image_label(fit_in_view=False))

            # menu actions
            self.ui.actionOpen_Folder.triggered.connect(self.open_folder)
            self.ui.actionClose_Folder.triggered.connect(self.close_folder)
            self.ui.actionCrop_All.triggered.connect(self.crop_all)
            self.ui.actionAbout.triggered.connect(self.about)
            
            # buttons
            self.ui.deleteRectangleButton.clicked.connect(self.delete_rectangle_button_clicked)

            # image selection changed
            self.ui.imagesListWidget.currentItemChanged.connect(self.image_selection_changed)
            self.ui.rectanglesListWidget.currentItemChanged.connect(self.rectangle_selection_changed)


        def enable(self):
            self.ui.actionOpen_Folder.setEnabled(False)
            self.ui.actionClose_Folder.setEnabled(True)
            self.ui.actionCrop_All.setEnabled(True)
            self.ui.deleteRectangleButton.setEnabled(False)

        
        def disable(self):
            self.ui.actionOpen_Folder.setEnabled(True)
            self.ui.actionClose_Folder.setEnabled(False)
            self.ui.actionCrop_All.setEnabled(False)
            self.ui.deleteRectangleButton.setEnabled(False)


        def resizeEvent(self, event):
            self.update_image_label(fit_in_view=False)


        def keyPressEvent(self, event):
            if event.key() == QtCore.Qt.Key_Escape:
                self.model.current_rectangle = []
            event.accept()


        def about(self):
            gh = "LukasBommes/Quad-Cropper"
            about_text = "QuadCropper<br><br>" \
                + "Author: Lukas Bommes<br>" \
                + "Organization: Helmholtz Institute Erlangen-Nürnberg for Renewable Energy (HI ERN)<br>" \
                + "GitHub: <a href='https://github.com/{gh}'>{gh}</a><br>".format(gh=gh)
            QMessageBox.about(
                self,
                "About QuadCropper",
                about_text
            )


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
                    self.model.rectangles = defaultdict(dict, json.load(file))
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
            # select output directory
            output_dir = QFileDialog.getExistingDirectory(
                self, caption="Select Output Directory", options=QFileDialog.ShowDirsOnly)
            if output_dir == "":
                return
            # crop and rectify annotated regions from current image
            for image_name, rectangles in self.model.rectangles.items():
                image_file = os.path.join(self.model.image_dir, image_name)
                image = self.load_image(image_file)
                image_file_name, image_file_ext = os.path.splitext(os.path.basename(image_file))
                for rectangle_id, rectangle in rectangles.items():
                    rectangle = sort_cw(np.array(rectangle))
                    rectangle = rectangle.reshape(4, 1, 2)
                    image_cropped, _ = crop_module(image, rectangle, crop_width=None, crop_aspect=None, rotate_mode=None)
                    cv2.imwrite(os.path.join(output_dir, "{}_{}{}".format(image_file_name, rectangle_id, image_file_ext)), image_cropped)
            print("Cropped annotated rectangles for all images in opened folder")


        def get_image_files(self):
            image_files = []
            for file_type in ["jpg", "JPG", "png", "PNG", "tiff", "TIFF"]:
                files = sorted(glob.glob(os.path.join(self.model.image_dir, "*.{}".format(file_type))))
                image_files.extend(files)
            self.model.image_files = image_files

        
        @Slot()
        def update_image_list(self, image_files):
            self.ui.imagesListWidget.clear()
            for image_file in image_files:
                file_name = os.path.basename(image_file)
                self.ui.imagesListWidget.addItem(file_name)


        @Slot()
        def image_selection_changed(self):
            self.model.current_rectangle = []
            self.model.current_image = None
            self.model.selected_rectangle = None
            # get name of selected image
            current = self.ui.imagesListWidget.currentItem()
            if not current:
                return
            selected_image_file = current.text()
            # load selected image
            image_file = os.path.join(self.model.image_dir, selected_image_file)
            image = self.load_image(image_file)
            height, width, _ = image.shape[:3]
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            bytesPerLine = 3 * width
            qt_image = QImage(image_rgb.data, width, height, bytesPerLine, QImage.Format_RGB888)
            self.model.current_image = {
                "filename": selected_image_file,
                "pixmap": QPixmap(qt_image),
                "image": image,
            }


        def load_image(self, image_file):
            return cv2.imread(image_file)


        @Slot()
        def update_image_label(self, fit_in_view):
            if not self.model.current_image:
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
                for rectangle_id, rectangle in rectangles.items():
                    polygon = QPolygonF()
                    if self.model.selected_rectangle and rectangle_id == self.model.selected_rectangle:
                        painter.setBrush(QColor(255, 128, 0, 255))
                    else:
                        painter.setBrush(QColor(0, 255, 0, 255))
                    for corner in sort_cw(np.array(rectangle)):
                        painter.drawEllipse(QPointF(*corner), 5, 5)
                        polygon.append(QPointF(*corner))
                    if self.model.selected_rectangle and rectangle_id == self.model.selected_rectangle:
                        painter.setBrush(QColor(255, 128, 0, 100))
                    else:
                        painter.setBrush(QColor(0, 255, 0, 100))
                    painter.drawConvexPolygon(polygon)
                painter.end()            

            self.viewer.setPhoto(pixmap, fit_in_view)


        def photoClicked(self, pos):
            self.add_point_to_current_rectangle(pos.x(), pos.y())


        def add_point_to_current_rectangle(self, x, y):
            current_rectangle_copy = self.model.current_rectangle.copy()
            current_rectangle_copy.append((x, y))
            #print("self.model.current_rectangle: ", current_rectangle_copy)
            self.model.current_rectangle = current_rectangle_copy
            if len(current_rectangle_copy) < 4:
                return
            self.create_new_rectangle()
            

        def create_new_rectangle(self):
            image_file = self.model.current_image["filename"]
            rectangles_copy = self.model.rectangles.copy()
            new_id = str(uuid.uuid4())[:8]
            rectangles_copy[image_file][new_id] = self.model.current_rectangle
            self.model.rectangles = rectangles_copy
            self.model.current_rectangle = []
            #print("self.model.current_rectangle: ", self.model.current_rectangle)
            #print("self.model.rectangles: ", self.model.rectangles)

        
        @Slot()
        def save_rectangles(self):
            if not self.model.image_dir:
                return
            # save to disk
            with open(os.path.join(self.model.image_dir, "meta.json"), "w") as file:
                json.dump(self.model.rectangles, file)


        @Slot()
        def update_rectangle_list(self):
            self.ui.rectanglesListWidget.clear()
            if not self.model.current_image:
                return
            try:
                file_name = self.model.current_image["filename"]
                rectangles = self.model.rectangles[file_name]
            except KeyError: # no annotations yet
                pass
            else:            
                for rectangle_id in rectangles.keys():
                    self.ui.rectanglesListWidget.addItem(rectangle_id)


        @Slot()
        def rectangle_selection_changed(self):
            # get selected rectangle from list
            self.model.selected_rectangle = None
            current = self.ui.rectanglesListWidget.currentItem()
            if not current:
                return
            self.model.selected_rectangle = current.text()


        @Slot()
        def selected_rectangle_changed(self):
            if self.model.selected_rectangle:
                self.ui.deleteRectangleButton.setEnabled(True)
            else:
                self.ui.deleteRectangleButton.setEnabled(False)


        @Slot()
        def delete_rectangle_button_clicked(self):
            if not self.model.current_image:
                return
            if not self.model.selected_rectangle:
                return
            #print("Deleting {}".format(self.model.selected_rectangle))
            # delete from rectangles
            try:
                image_file = self.model.current_image["filename"]
                rectangles_copy = self.model.rectangles.copy()
            except KeyError:
                pass
            else:
                del rectangles_copy[image_file][self.model.selected_rectangle]
                self.model.rectangles = rectangles_copy



    class Model(QObject):
        rectangles_changed = Signal(object)
        current_rectangle_changed = Signal(object)
        current_image_changed = Signal(object)
        image_files_changed = Signal(list)
        selected_rectangle_changed = Signal(str)

        def __init__(self):
            super().__init__()
            self._image_dir = None
            self._image_files = []
            self._rectangles = defaultdict(dict)
            self._current_rectangle = []
            self._current_image = None
            self._selected_rectangle = None

        def reset(self):
            self.image_dir = None
            self.image_files = []
            self.rectangles = defaultdict(dict)
            self.current_rectangle = []
            self.current_image = None
            self.selected_rectangle = None

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
            #print("image_files_changed emitted")

        @property
        def rectangles(self):
            return self._rectangles

        @rectangles.setter
        def rectangles(self, value):
            self._rectangles = value
            self.rectangles_changed.emit(value)
            #print("rectangles_changed emitted")

        @property
        def current_rectangle(self):
            return self._current_rectangle

        @current_rectangle.setter
        def current_rectangle(self, value):
            self._current_rectangle = value
            self.current_rectangle_changed.emit(value)
            #print("current_rectangle_changed emitted")

        @property
        def current_image(self):
            return self._current_image

        @current_image.setter
        def current_image(self, value):
            self._current_image = value
            self.current_image_changed.emit(value)
            #print("current_image_changed emitted")

        @property
        def selected_rectangle(self):
            return self._selected_rectangle

        @selected_rectangle.setter
        def selected_rectangle(self, value):
            self._selected_rectangle = value
            self.selected_rectangle_changed.emit(value)
            #print("selected_rectangle_changed emitted")


    app = QApplication(sys.argv)
    window = MainWindow()
    screen = window.screen()
    window.resize(screen.availableSize() * 0.5)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
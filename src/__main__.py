def main():
    import sys
    import os
    import glob
    import json
    import uuid
    from collections import defaultdict

    import numpy as np
    import cv2

    from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QSizePolicy
    from PySide6.QtCore import Qt, QObject, Signal, QSettings, QPointF
    from PySide6.QtGui import QPainter, QColor, QPolygonF
    from src.ui_mainwindow import Ui_MainWindow
    from src.viewer import ImageViewer, PreviewViewer
    from src.utils import sort_cw, crop_module, image2pixmap



    class MainWindow(QMainWindow):
        def __init__(self):
            super(MainWindow, self).__init__()
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)
            self.setWindowTitle("QuadCropper")            
            self.model = Model()
            self.disable()

            # image viewer
            self.viewer = self.ui.graphicsView

            # preview viewer
            self.preview_viewer = PreviewViewer(self)
            sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.preview_viewer.sizePolicy().hasHeightForWidth())
            self.preview_viewer.setSizePolicy(sizePolicy)
            self.ui.verticalLayout.addWidget(self.preview_viewer)

            # application presets
            self.settings = QSettings('Lukas Bommes', 'QuadCropper')

            # signals
            self.model.current_image_changed.connect(lambda _: self.update_image_label(fit_in_view=True))
            self.model.current_image_changed.connect(self.update_quad_list)
            self.model.current_image_changed.connect(self.update_preview)
            self.model.current_quad_changed.connect(lambda _: self.update_image_label(fit_in_view=False))
            self.model.quads_changed.connect(self.save_quads)
            self.model.quads_changed.connect(lambda _: self.update_image_label(fit_in_view=False))    
            self.model.quads_changed.connect(self.update_quad_list)    
            self.model.image_files_changed.connect(self.update_image_list)
            self.model.selected_quad_changed.connect(self.selected_quad_changed)
            self.model.selected_quad_changed.connect(lambda _: self.update_image_label(fit_in_view=False))
            self.model.selected_quad_changed.connect(self.update_preview)
            self.ui.autoPatchSizeCheckbox.stateChanged.connect(lambda value: setattr(self.model, 'auto_patch_size', bool(value)))
            self.model.auto_patch_size_changed.connect(lambda value: self.auto_patch_size_changed(value))
            self.model.auto_patch_size_changed.connect(self.ui.autoPatchSizeCheckbox.setChecked)
            self.model.auto_patch_size_changed.connect(self.update_preview)
            self.model.patch_width_changed.connect(self.ui.patchWidthSpinBox.setValue)
            self.model.patch_width_changed.connect(self.update_preview)
            self.ui.patchWidthSpinBox.valueChanged.connect(lambda value: setattr(self.model, 'patch_width', value))
            self.model.patch_height_changed.connect(self.ui.patchHeightSpinBox.setValue)
            self.model.patch_height_changed.connect(self.update_preview)
            self.ui.patchHeightSpinBox.valueChanged.connect(lambda value: setattr(self.model, 'patch_height', value))

            # menu actions
            self.ui.actionOpen_Folder.triggered.connect(self.open_folder)
            self.ui.actionClose_Folder.triggered.connect(self.close_folder)
            self.ui.actionAbout.triggered.connect(self.about)
            
            # buttons
            self.ui.deleteSelectedQuadButton.clicked.connect(self.delete_selected_quad_button_clicked)
            self.ui.deleteAllQuadsButton.clicked.connect(self.delete_all_quads_button_clicked)
            self.ui.cropAllButton.clicked.connect(self.crop_all)

            # image selection changed
            self.ui.imagesListWidget.currentItemChanged.connect(self.image_selection_changed)
            self.ui.quadsListWidget.currentItemChanged.connect(self.quad_selection_changed)

            # restore settings
            self.restore_settings()


        def enable(self):
            self.ui.actionOpen_Folder.setEnabled(False)
            self.ui.actionClose_Folder.setEnabled(True)
            self.ui.deleteSelectedQuadButton.setEnabled(False)
            self.ui.deleteAllQuadsButton.setEnabled(False)
            self.ui.cropAllButton.setEnabled(True)
            self.ui.autoPatchSizeCheckbox.setEnabled(True)
            self.ui.patchWidthSpinBox.setEnabled(False)
            self.ui.patchHeightSpinBox.setEnabled(False)
            self.ui.patchHeightLabel.setEnabled(False)
            self.ui.patchWidthLabel.setEnabled(False)

        
        def disable(self):
            self.ui.actionOpen_Folder.setEnabled(True)
            self.ui.actionClose_Folder.setEnabled(False)            
            self.ui.deleteSelectedQuadButton.setEnabled(False)
            self.ui.deleteAllQuadsButton.setEnabled(False)
            self.ui.cropAllButton.setEnabled(False)
            self.ui.autoPatchSizeCheckbox.setEnabled(False)
            self.ui.patchWidthSpinBox.setEnabled(False)
            self.ui.patchHeightSpinBox.setEnabled(False)
            self.ui.patchHeightLabel.setEnabled(False)
            self.ui.patchWidthLabel.setEnabled(False)


        def resizeEvent(self, event):
            self.update_image_label(fit_in_view=False)


        def keyPressEvent(self, event):
            if event.key() == Qt.Key_Escape:
                self.model.current_quad = []
            event.accept()


        def closeEvent(self, event):
            self.settings.setValue('window size', self.size())
            self.settings.setValue('window position', self.pos())
            print("Saved presets")
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


        def restore_settings(self):
            window_size = self.settings.value('window size')
            if window_size:
                self.resize(window_size)
            window_position = self.settings.value('window position')
            if window_position:          
                self.move(window_position)


        def open_folder(self):
            dir = QFileDialog.getExistingDirectory(
                self, caption="Open Dataset", options=QFileDialog.ShowDirsOnly)
            if dir == "":
                return
            self.model.image_dir = dir
            # check if meta.json is available and load into model
            try:
                with open(os.path.join(dir, "meta.json"), "r") as file:
                    self.model.quads = defaultdict(dict, json.load(file))
            except FileNotFoundError:
                pass
            self.get_image_files()
            self.enable()
            print("Dataset opened")


        def close_folder(self):
            self.model.reset()
            print(self.model.auto_patch_size)
            self.disable()
            print("Dataset closed")


        def get_num_quads(self, image_file=None):
            num_quads = 0
            if image_file:
                try:
                    num_quads = sum([len(q) for q in self.model.quads[image_file].values()])
                except KeyError:
                    pass
            else:
                num_quads = sum([len(q) for q in self.model.quads.values()])
            return num_quads


        def crop_all(self):
            # select output directory
            output_dir = QFileDialog.getExistingDirectory(
                self, caption="Select Output Directory", options=QFileDialog.ShowDirsOnly)
            if output_dir == "":
                return
            # crop and rectify annotated regions from current image
            if self.model.auto_patch_size:
                crop_width = None
                crop_aspect = None
            else:
                crop_width = self.model.patch_width
                crop_aspect = self.model.patch_height / self.model.patch_width
            for image_name, quads in self.model.quads.items():
                image_file = os.path.join(self.model.image_dir, image_name)
                image = self.load_image(image_file)
                image_file_name, image_file_ext = os.path.splitext(os.path.basename(image_file))
                for quad_id, quad in quads.items():
                    quad = sort_cw(np.array(quad))
                    quad = quad.reshape(4, 1, 2)
                    image_cropped, _ = crop_module(
                        image, quad, crop_width=crop_width, crop_aspect=crop_aspect, rotate_mode=None)
                    cv2.imwrite(os.path.join(output_dir, "{}_{}{}".format(
                        image_file_name, quad_id, image_file_ext)), image_cropped)
            print("Cropped annotated quads for all images in opened folder")


        def update_preview(self):
            # update crop preview image when quad selection changes
            self.preview_viewer.setImage(pixmap=None)
            if not self.model.current_image:
                return
            if self.model.auto_patch_size:
                crop_width = None
                crop_aspect = None
            else:
                crop_width = self.model.patch_width
                crop_aspect = self.model.patch_height / self.model.patch_width
            image = self.model.current_image["image"]
            image_name = self.model.current_image["filename"]
            try:                
                quad = self.model.quads[image_name][self.model.selected_quad]
            except KeyError:
                return
            quad = sort_cw(np.array(quad))
            quad = quad.reshape(4, 1, 2)
            image_cropped, _ = crop_module(
                image, quad, crop_width=crop_width, crop_aspect=crop_aspect, rotate_mode=None)
            self.preview_viewer.setImage(pixmap=image2pixmap(image_cropped), fit_in_view=True)


        def get_image_files(self):
            image_files = []
            for file_type in ["jpg", "jpeg", "png"]:
                files = sorted(glob.glob(os.path.join(self.model.image_dir, "*.{}".format(file_type))))
                files_upper = sorted(glob.glob(os.path.join(self.model.image_dir, "*.{}".format(file_type.upper()))))
                image_files.extend(files)
                image_files.extend(files_upper)
            self.model.image_files = list(set(image_files))  # remove duplicates

        
        def update_image_list(self, image_files):
            self.ui.imagesListWidget.clear()
            for image_file in image_files:
                file_name = os.path.basename(image_file)
                self.ui.imagesListWidget.addItem(file_name)


        def image_selection_changed(self):
            self.model.current_quad = []
            self.model.current_image = None
            self.model.selected_quad = None
            # get name of selected image
            current = self.ui.imagesListWidget.currentItem()
            if not current:
                return
            selected_image_file = current.text()
            # load selected image
            image_file = os.path.join(self.model.image_dir, selected_image_file)
            image = self.load_image(image_file)
            self.model.current_image = {
                "filename": selected_image_file,
                "pixmap": image2pixmap(image),
                "image": image,
            }


        def load_image(self, image_file):
            return cv2.imread(image_file)


        def update_image_label(self, fit_in_view):
            if not self.model.current_image:
                self.viewer.setImage(None)
                return
            
            pixmap = self.model.current_image["pixmap"].copy()

            # draw current quad
            painter = QPainter(pixmap)
            painter.setBrush(Qt.red)
            for corner in self.model.current_quad:
                painter.drawEllipse(QPointF(*corner), 5, 5)
            painter.end()

            # draw quads
            try:
                image_file = self.model.current_image["filename"]
                quads = self.model.quads[image_file]
            except KeyError:
                pass
            else:
                painter = QPainter(pixmap)
                for quad_id, quad in quads.items():
                    polygon = QPolygonF()
                    if self.model.selected_quad and quad_id == self.model.selected_quad:
                        painter.setBrush(QColor(255, 128, 0, 255))
                    else:
                        painter.setBrush(QColor(0, 255, 0, 255))
                    for corner in sort_cw(np.array(quad)):
                        painter.drawEllipse(QPointF(*corner), 5, 5)
                        polygon.append(QPointF(*corner))
                    if self.model.selected_quad and quad_id == self.model.selected_quad:
                        painter.setBrush(QColor(255, 128, 0, 100))
                    else:
                        painter.setBrush(QColor(0, 255, 0, 100))
                    painter.drawConvexPolygon(polygon)
                painter.end()            

            self.viewer.setImage(pixmap, fit_in_view)


        def imageClicked(self, pos):
            self.add_point_to_current_quad(pos.x(), pos.y())


        def add_point_to_current_quad(self, x, y):
            current_quad_copy = self.model.current_quad.copy()
            current_quad_copy.append((x, y))
            #print("self.model.current_quad: ", current_quad_copy)
            self.model.current_quad = current_quad_copy
            if len(current_quad_copy) < 4:
                return
            self.create_new_quad()
            

        def create_new_quad(self):
            image_file = self.model.current_image["filename"]
            quads_copy = self.model.quads.copy()
            new_id = str(uuid.uuid4())[:8]
            quads_copy[image_file][new_id] = self.model.current_quad
            self.model.quads = quads_copy
            self.model.current_quad = []
            #print("self.model.current_quad: ", self.model.current_quad)
            #print("self.model.quads: ", self.model.quads)

        
        def save_quads(self):
            if not self.model.image_dir:
                return
            # save to disk
            with open(os.path.join(self.model.image_dir, "meta.json"), "w") as file:
                json.dump(self.model.quads, file)


        def update_quad_list(self):
            self.ui.quadsListWidget.clear()
            if not self.model.current_image:
                return
            try:
                file_name = self.model.current_image["filename"]
                quads = self.model.quads[file_name]
            except KeyError: # no annotations yet
                pass
            else:            
                for quad_id in quads.keys():
                    self.ui.quadsListWidget.addItem(quad_id)
                # update buttons
                if self.get_num_quads(file_name):
                    self.ui.deleteAllQuadsButton.setEnabled(True)
                else:
                    self.ui.deleteAllQuadsButton.setEnabled(False)


        def quad_selection_changed(self):
            # get selected quad from list
            self.model.selected_quad = None
            current = self.ui.quadsListWidget.currentItem()
            if not current:
                return
            self.model.selected_quad = current.text()


        def selected_quad_changed(self):
            if self.model.selected_quad:
                self.ui.deleteSelectedQuadButton.setEnabled(True)
            else:
                self.ui.deleteSelectedQuadButton.setEnabled(False)


        def delete_selected_quad_button_clicked(self):
            if not self.model.current_image:
                return
            if not self.model.selected_quad:
                return
            #print("Deleting {}".format(self.model.selected_quad))
            # delete from quads
            try:
                image_file = self.model.current_image["filename"]
                quads_copy = self.model.quads.copy()
            except KeyError:
                pass
            else:
                del quads_copy[image_file][self.model.selected_quad]
                self.model.quads = quads_copy

        
        def delete_all_quads_button_clicked(self):
            if not self.model.image_dir:
                return
            try:
                image_file = self.model.current_image["filename"]
                quads_copy = self.model.quads.copy()
            except KeyError:
                pass
            else:
                del quads_copy[image_file]
                self.model.quads = quads_copy


        def auto_patch_size_changed(self, auto_patch_size):
            self.ui.patchWidthSpinBox.setEnabled(not auto_patch_size)
            self.ui.patchHeightSpinBox.setEnabled(not auto_patch_size)



    class Model(QObject):
        quads_changed = Signal(object)
        current_quad_changed = Signal(object)
        current_image_changed = Signal(object)
        image_files_changed = Signal(list)
        selected_quad_changed = Signal(str)
        auto_patch_size_changed = Signal(bool)
        patch_width_changed = Signal(int)
        patch_height_changed = Signal(int)

        def __init__(self):
            super().__init__()
            self._image_dir = None
            self._image_files = []
            self._quads = defaultdict(dict)
            self._current_quad = []
            self._current_image = None
            self._selected_quad = None
            self._auto_patch_size = True
            self._patch_width = 100
            self._patch_height = 100

        def reset(self):
            self.image_dir = None
            self.image_files = []
            self.quads = defaultdict(dict)
            self.current_quad = []
            self.current_image = None
            self.selected_quad = None
            self.auto_patch_size = True
            self.patch_width = 100
            self.patch_height = 100

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
        def quads(self):
            return self._quads

        @quads.setter
        def quads(self, value):
            self._quads = value
            self.quads_changed.emit(value)
            #print("quads_changed emitted")

        @property
        def current_quad(self):
            return self._current_quad

        @current_quad.setter
        def current_quad(self, value):
            self._current_quad = value
            self.current_quad_changed.emit(value)
            #print("current_quad_changed emitted")

        @property
        def current_image(self):
            return self._current_image

        @current_image.setter
        def current_image(self, value):
            self._current_image = value
            self.current_image_changed.emit(value)
            #print("current_image_changed emitted")

        @property
        def selected_quad(self):
            return self._selected_quad

        @selected_quad.setter
        def selected_quad(self, value):
            self._selected_quad = value
            self.selected_quad_changed.emit(value)
            #print("selected_quad_changed emitted")

        @property
        def auto_patch_size(self):
            return self._auto_patch_size

        @auto_patch_size.setter
        def auto_patch_size(self, value):
            self._auto_patch_size = value
            self.auto_patch_size_changed.emit(value)

        @property
        def patch_width(self):
            return self._patch_width

        @patch_width.setter
        def patch_width(self, value):
            self._patch_width = value
            self.patch_width_changed.emit(value)

        @property
        def patch_height(self):
            return self._patch_height

        @patch_height.setter
        def patch_height(self, value):
            self._patch_height = value
            self.patch_height_changed.emit(value)


    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
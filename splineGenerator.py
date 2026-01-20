### Matt Rafferty
### 2026 - Version 1.0
### Spline Generation Tool

import cv2
import numpy as np
import sys
from PySide6.QtWidgets import *
from PySide6 import QtCore
from PySide6.QtGui import *

class SplineGenerator(QDialog):
    def __init__(self, parent=None):
        self.imagePath = None
        self.loadedImage = None
        self.blurEnabled = False
        self.invertColour = False
        self.contours = None

        super(SplineGenerator, self).__init__(parent)
        self.setWindowTitle("Image To Spline Tool")

        self.resize(300, 150)
        
        self.mainLayout = QVBoxLayout()
        self.mainLayout.setSpacing(2)
        self.mainLayout.setContentsMargins(2,2,2,2)
        self.setLayout(self.mainLayout)
        self.loadImageButton = QPushButton()
        self.loadImageButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.loadImageButton.setIcon(QIcon.fromTheme("document-open"))
        self.loadImageButton.setText("Load Image")
        self.mainLayout.addWidget(self.loadImageButton)
        self.sourceImagePreview = QLabel("No image loaded")
        self.sourceImagePreview.setAlignment(Qt.AlignCenter)
        self.sourceImagePreview.setScaledContents(True)      
        self.sourceImagePreview.setMinimumSize(100, 100)
        self.sourceImagePreview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.mainLayout.addWidget(self.sourceImagePreview)

        self.currentContoursLabel = QLabel('Current Contours Detected: 0')
        self.currentContoursLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.mainLayout.addWidget(self.currentContoursLabel)

        settingsGroup = QGroupBox()
        settingsLayout = QVBoxLayout()
        settingsLayout.setSpacing(2)
        settingsLayout.setContentsMargins(2,2,2,2)
        settingsGroup.setLayout(settingsLayout)
        self.mainLayout.addWidget(settingsGroup)

        self.invertColourCheck = QCheckBox('Invert Colour?')
        self.invertColourCheck.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        settingsLayout.addWidget(self.invertColourCheck)

        blockSizeHBox = QHBoxLayout()
        blockSizeHBox.setSpacing(2)
        blockSizeHBox.setContentsMargins(2,2,2,2)
       
        blockSizeLabel = QLabel('Block Size')
        blockSizeLabel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.blockSizeSlider = QSlider(Qt.Horizontal, minimum=0, maximum=100, value=50)
        self.blockSizeSlider.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        blockSizeHBox.addWidget(blockSizeLabel)
        blockSizeHBox.addWidget(self.blockSizeSlider)
        settingsLayout.addLayout(blockSizeHBox)

        constantHBox = QHBoxLayout()
        constantHBox.setSpacing(2)
        constantHBox.setContentsMargins(2,2,2,2)
        constantLabel = QLabel('Constant')
        constantLabel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.constantSlider = QSlider(Qt.Horizontal, minimum=0, maximum=30, value=50)
        self.constantSlider.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        constantHBox.addWidget(constantLabel)
        constantHBox.addWidget(self.constantSlider)
        settingsLayout.addLayout(constantHBox)

        self.blurEnableCheck = QCheckBox('Blur Image?')
        self.blurEnableCheck.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        settingsLayout.addWidget(self.blurEnableCheck)

        blurHbox = QHBoxLayout()
        blurHbox.setSpacing(2)
        blurHbox.setContentsMargins(2,2,2,2)
        self.blurAmountLabel = QLabel('Blur Amount:')
        self.blurAmountLabel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.blurAmountLabel.setEnabled(False)
        self.blurAmountSlider = QSlider(Qt.Horizontal, minimum=0, maximum=100, value=50)
        self.blurAmountSlider.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.blurAmountSlider.setValue(1)
        self.blurAmountSlider.setEnabled(False)
        blurHbox.addWidget(self.blurAmountLabel)
        blurHbox.addWidget(self.blurAmountSlider)

        settingsLayout.addLayout(blurHbox)

        self.exportSplineButton = QPushButton("Export Spline")
        self.exportSplineButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.mainLayout.addWidget(self.exportSplineButton)

    def translate(self) -> None:
        '''
        Function to hook up UI callbacks
        '''
        self.loadImageButton.clicked.connect(self.uicb_loadImage)
        self.exportSplineButton.clicked.connect(self.uicb_exportSpline)
        self.blurAmountSlider.valueChanged.connect(self.uicb_blurAmountChanged)
        self.blurEnableCheck.stateChanged.connect(self.uicb_toggleBlur)
        self.blockSizeSlider.valueChanged.connect(self.uicb_updateContourThreshold)
        self.constantSlider.valueChanged.connect(self.uicb_updateContourThreshold)
        self.invertColourCheck.stateChanged.connect(self.uicb_toggleInvertColour)

    def uicb_toggleInvertColour(self, state : bool) -> None:
        '''
        UI callback for toggling invert colour
        param state: The state of the checkbox
        '''
        self.invertColour = state
        self.updatePreview()

    def uicb_updateContourThreshold(self) -> None:
        '''
        UI Callback for updating the contour detection threashold
        '''
        self.updatePreview()

    def uicb_toggleBlur(self, state : bool) -> None:
        '''
        UI callback for toggling blur enabled
        param state: The state of the checkbox
        '''
        self.blurEnabled = state
        self.blurAmountSlider.setEnabled(state)
        self.blurAmountLabel.setEnabled(state)
        self.updatePreview()

    def uicb_blurAmountChanged(self) -> None:
        '''
        UI Callback for changing the blur amount
        '''
        self.updatePreview()

    def updatePreview(self) -> None:
        '''
        Function to update the preview window when settings are changed
        '''
        previewImage = self.loadedImage
        previewImage = cv2.cvtColor(previewImage, cv2.COLOR_BGR2GRAY)
        if self.invertColour:
            previewImage = cv2.bitwise_not(previewImage)    
        
        if self.blurEnabled:
            kernelSize = self.blurAmountSlider.value()
            if kernelSize % 2 == 0:
                kernelSize += 1 
            previewImage = cv2.GaussianBlur(previewImage, (kernelSize, kernelSize), 0)
        _, binary = cv2.threshold(previewImage, 127, 255, cv2.THRESH_BINARY)

        blockSize = 11 + 2*self.blockSizeSlider.value()
        constant = self.constantSlider.value() - 10

        binary = cv2.adaptiveThreshold(previewImage, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, blockSize,constant) 
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        self.contours = contours
        self.currentContoursLabel.setText(f'Current Contours Detected: {len(contours)}')
        previewImage = cv2.cvtColor(previewImage, cv2.COLOR_GRAY2BGR)
        cv2.drawContours(previewImage, contours, -1, (0, 0, 255), 4)
        qImage = QImage(previewImage.data, previewImage.shape[1], previewImage.shape[0],
                  previewImage.strides[0], QImage.Format_BGR888)
    
        pixmap = QPixmap.fromImage(qImage)
        
        self.sourceImagePreview.setPixmap(pixmap.scaled(self.sourceImagePreview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def uicb_exportSpline(self) -> None:
        '''
        UI callback to export the detected contours as spline coords in csv
        '''
        if not self.imagePath:
            QMessageBox.warning(window, 'No Image Loaded', 'Please load an image file before exporting spline', QMessageBox.Ok)
            return
        
        if self.loadedImage is None:
            QMessageBox.warning(window, 'Loaded Image Corrupted', 'An image is loaded but its data cannot be read.', QMessageBox.Ok)
            return

        if self.contours is None:
            QMessageBox.warning(window, 'No Contours Found', 'No contours were detected in the image, please adjust your settings.', QMessageBox.Ok)
            return

        contour = max(self.contours, key=cv2.contourArea)
        points = contour[:, 0, :].astype(float)

        if not np.allclose(points[0], points[-1]):
            points = np.vstack([points, points[0]])

        splinePoints = np.column_stack([points[:, 0], points[:, 1], np.zeros(len(points))])
    
        csvHeader = "Index,X,Y,Z\n"
        csvRows = "\n".join([f"{i},{p[0]},{p[1]},{p[2]}" for i, p in enumerate(splinePoints)])
        csvContent = csvHeader + csvRows

        outputFile = QFileDialog.getSaveFileName(self, "Save Spline Points", "", "CSV Files (*.csv)")
        if not outputFile[0]:
            return
        with open(outputFile[0], 'w') as f:
            f.write(csvContent)

    def uicb_loadImage(self) -> None:
        '''
        UI callback to show the file dialog for the user to select an image
        '''
        imagePath = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if not imagePath[0]:
            return
        
        self.imagePath = imagePath[0]

        loadedImage = cv2.imread(imagePath[0])
        if loadedImage is None:
            QMessageBox.warning(window, 'Failed to read image file', 'Could not read image file, check if the file is corrupted!', QMessageBox.Ok)
            return
        self.loadedImage = loadedImage
        self.updatePreview()


        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('splineIcon.png'))
    window = SplineGenerator()
    
    window.translate()
    window.show()
    sys.exit(app.exec())
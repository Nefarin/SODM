import sys
import imp
import vtk
import gdcm
import os
import re
import vtkgdcm
import time

from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QApplication
from MainWindowGen import Ui_MainWindow
from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from DicomLoader import DicomLoader
from DebugPathBuilder import DebugPathBuilder

class AppWindow(QtGui.QMainWindow):
    def __init__(self):
        self.importSrc()
        self.initGUI()
        self.initToolbar()
        self.initConnections()


        #vtk.vtkGDCMImageReader()
        #self.dicomReader = vtk.vtkDICOMImageReader()
        #self.dicomReader.SetFileName(DebugPathBuilder.appendPath(DebugPathBuilder.resourcePath(), "3.dcm"))
        #self.dicomReader.Update()

        #self.viewer= vtk.vtkImageViewer()
        #viewer = self.viewer
        #viewer.SetInputConnection(self.dicomReader.GetOutputPort())
        #self.vtkWidget.GetRenderWindow().AddRenderer(viewer.GetRenderer())
        #self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()
        #self.iren.Initialize()





    def importSrc(self):
        # will be shown as errors in pyCharm
        pass
    def initConnections(self):
        self.connect(self.ui.actionLoad, QtCore.SIGNAL("triggered()"), self.loadSingleFile)

    def initGUI(self):
        QtGui.QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Simple Dicom Viewer")

        #self.dicomReader = vtk.vtkDICOMImageReader()
        #self.dicomReader = vtkgdcm.vtkGDCMImageReader()
        self.vtkWidget = QVTKRenderWindowInteractor(self.ui.imageFrame)
        self.ui.imageLayout.removeWidget(self.ui.dicomSlider)
        self.ui.imageLayout.addWidget(self.vtkWidget)
        self.ui.imageLayout.addWidget(self.ui.dicomSlider)

        self.disableSlider()
        #self.ui.imageLayout.addWidget(tempWidget)

        self.viewer= vtk.vtkImageViewer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.viewer.GetRenderer())
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()

        #self.iren.Initialize()

    def initToolbar(self):
        self.actions = Actions(self)

    def loadSingleFile(self):
        loader = DicomLoader(self, "file")
        loader.loadFile()

        if loader.accepted:
            self.disableSlider()
            self.dicomReader = vtkgdcm.vtkGDCMImageReader()
            self.dicomReader.SetFileName(str(loader.selectedFile))

            self.dicomReader.Update()
            imageData = self.dicomReader.GetOutput()

            size = imageData.GetDimensions()
            width = size[0]
            height = size[1]
            self.ui.imageFrame.setMaximumSize(QtCore.QSize(width, height))
            self.ui.imageFrame.setMinimumSize(QtCore.QSize(width, height))


            self.viewer.SetInputConnection(self.dicomReader.GetOutputPort())
            self.viewer.SetZSlice(0)
            self.iren.ReInitialize()
            self.iren.Render()
            self.iren.Start()

    def disableSlider(self):
        self.ui.dicomSlider.setDisabled(True)
        self.ui.dicomSlider.setValue(0)
        self.ui.dicomSlider.disconnect(self.ui.dicomSlider, QtCore.SIGNAL("valueChanged(int)"), self.sliderMoved)

    @QtCore.pyqtSlot(int)
    def sliderMoved(self, value):
        try:
            self.viewer.SetZSlice(value)
            self.iren.Render()
        except:
            raise ValueError

    def enableSlider(self, max):
        self.ui.dicomSlider.setEnabled(True)
        self.ui.dicomSlider.setValue(0)
        self.ui.dicomSlider.setMinimum(0)
        self.ui.dicomSlider.setMaximum(max)
        self.ui.dicomSlider.connect(self.ui.dicomSlider, QtCore.SIGNAL("valueChanged(int)"), self.sliderMoved)
    def loadFolder(self):
        loader = DicomLoader(self, "series")
        loader.loadFile()

        if loader.accepted:
            self.dicomReader = vtkgdcm.vtkGDCMImageReader()
            regex = re.compile(r'.+\.dcm')
            files = [x for x in os.listdir(loader.selectedFolder) if re.match(regex, x)]
            self.seriesSize = len(files)
            temp = vtk.vtkStringArray()
            temp.SetNumberOfValues(len(files))
            i = 0
            for file in sorted(files):
                temp.SetValue(i, os.path.join(str(loader.selectedFolder), file))
                i = i + 1
            self.dicomReader.SetFileNames(temp)
            self.dicomReader.Update()

            imageData = self.dicomReader.GetOutput()
            size = imageData.GetDimensions()
            width = size[0]
            height = size[1]
            self.ui.imageFrame.setMaximumSize(QtCore.QSize(width, height))
            self.ui.imageFrame.setMinimumSize(QtCore.QSize(width, height))

            self.viewer.SetInputConnection(self.dicomReader.GetOutputPort())
            self.iren.ReInitialize()

            self.enableSlider(self.seriesSize-1)
            self.ui.dicomSlider.setFocus()

class Actions(object):
    def __init__(self, parent):
        self.parent = parent

        self.loadSingleAction = QtGui.QAction("Load..", parent.ui.toolBar)
        parent.ui.toolBar.addAction(self.loadSingleAction)
        self.loadSingleAction.connect(self.loadSingleAction, QtCore.SIGNAL("triggered()"), self.loadSingleFile)

        self.loadFolderAction = QtGui.QAction("Load Series..", parent.ui.toolBar)
        parent.ui.toolBar.addAction(self.loadFolderAction)
        self.loadFolderAction.connect(self.loadFolderAction, QtCore.SIGNAL("triggered()"), self.loadFolder)


    def loadSingleFile(self):
        return self.parent.loadSingleFile()

    def loadFolder(self):
        return self.parent.loadFolder()

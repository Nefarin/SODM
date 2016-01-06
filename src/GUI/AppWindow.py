import sys
import imp
import vtk
import gdcm
import vtkgdcm

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
        self.connect(self.ui.actionLoad, QtCore.SIGNAL("triggered()"), self.loadFile)

    def initGUI(self):
        QtGui.QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Simple Dicom Viewer")

        #self.dicomReader = vtk.vtkDICOMImageReader()
        self.dicomReader = vtkgdcm.vtkGDCMImageReader()
        self.vtkWidget = QVTKRenderWindowInteractor(self.ui.imageFrame)
        self.ui.imageLayout.addWidget(self.vtkWidget)

        self.viewer= vtk.vtkImageViewer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.viewer.GetRenderer())
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()
        #self.iren.Initialize()

    def initToolbar(self):
        self.actions = Actions(self)

    def loadFile(self):
        loader = DicomLoader(self)
        loader.loadFile()

        if loader.accepted:
            print("Accepted")
            print(loader.selectedFile)
            self.dicomReader.SetFileName(str(loader.selectedFile))


            self.dicomReader.Update()
            wtf = self.dicomReader.GetOutput()
            #print(wtf)
            size = self.ui.imageFrame.size()

            """
            interp = vtk.vtkImageResample()
            interp.SetInterpolationModeToLinear()
            interp.SetInput(wtf)
            interp.SetDimensionality(2)
            interp.SetAxisMagnificationFactor(0, 0.5)
            interp.SetAxisMagnificationFactor(1, 0.5)
            interp.Update()
            wtf = interp.GetOutput()
            """
            #wtf.SetDimensions(size.width()*0.5, size.height()*0.5, 1)
            #print(self.ui.imageFrame.size())

            toSize = wtf.GetDimensions()
            #print(toSize)
            width = toSize[0]
            height = toSize[1]
            #print(width)
            #print(height)

            self.ui.imageFrame.setMaximumSize(QtCore.QSize(width, height))
            self.ui.imageFrame.setMinimumSize(QtCore.QSize(width, height))
            #print(self.ui.imageFrame.maximumSize())
            #self.dicomReader.SetOutput(wtf)
            #self.dicomReader.Update()


            self.viewer.SetInputConnection(self.dicomReader.GetOutputPort())
            #self.viewer.SetSize(size.width(), size.height())
            #self.viewer.SetInput(wtf)
            #self.viewer.Render()
            #self.viewer.GetRenderer().ResetCamera()
            #self.viewer.Render()
            self.iren.ReInitialize()
            self.iren.Start()


        else:
            print('Rejected')


class Actions(object):
    def __init__(self, parent):
        self.parent = parent
        self.loadAction = QtGui.QAction("Load", parent.ui.toolBar)
        parent.ui.toolBar.addAction(self.loadAction)
        self.loadAction.connect(self.loadAction, QtCore.SIGNAL("triggered()"), self.loadFile)
    def loadFile(self):
        return self.parent.loadFile()

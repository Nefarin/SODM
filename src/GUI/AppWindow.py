import sys
import imp
import vtk
import gdcm
import os
import re
import vtkgdcm
import time
import thread
import threading
import Queue
import numpy
import numpy_support
import dicom
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import multiprocessing

from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QApplication
from MainWindowGen import Ui_MainWindow
from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from DicomLoader import DicomLoader
from DebugPathBuilder import DebugPathBuilder
from ProcessingThread import ProcessingThread

class AppWindow(QtGui.QMainWindow):
    def __init__(self, parent):
        self.parent = parent
        self.queue = Queue.Queue()
        self.processThread = ProcessingThread(self.queue)
        #self.processThread = threading.Thread(target=self.consumer.run())
        self.processThread.start()

        self.fileLoader = DicomLoader(self, "file")
        self.folderLoader = DicomLoader(self, "series")
        self.importSrc()
        self.initGUI()
        self.initToolbar()
        self.initConnections()


    def importSrc(self):
        # will be shown as errors in pyCharm
        pass

    def exit(self):
        self.close()

    def initConnections(self):
        self.connect(self.ui.actionLoad, QtCore.SIGNAL("triggered()"), self.loadSingleFile)
        self.connect(self.ui.actionExit, QtCore.SIGNAL("triggered()"), self.exit)

    def initGUI(self):
        QtGui.QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Simple Dicom Viewer")

        #self.dicomReader = vtk.vtkDICOMImageReader()
        #self.dicomReader = vtkgdcm.vtkGDCMImageReader()
        self.show()

        self.vtkWidget = QVTKRenderWindowInteractor(self.ui.imageFrame)
        self.vtkWidget.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        #self.ui.imageLayout.removeWidget(self.ui.dicomSlider)
        self.ui.imageLayout.addWidget(self.vtkWidget)
        #self.ui.imageLayout.addWidget(self.ui.dicomSlider)

        self.disableSlider()

        self.viewer= vtk.vtkImageViewer()
        #self.viewer.SetupInteractor(MyInteractor())
        self.vtkWidget.GetRenderWindow().AddRenderer(self.viewer.GetRenderer())
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()
        #self.iren.SetRenderWindow(self.vtkWidget.GetRenderWindow())


        self.drag = False
        self.iren.AddObserver("LeftButtonPressEvent", self.leftClick)
        self.iren.AddObserver("LeftButtonReleaseEvent", self.leftRelease)
        self.iren.AddObserver("EnterEvent", self.mouseEntered)
        self.iren.AddObserver("LeaveEvent", self.mouseLeft)
        self.iren.AddObserver("MouseMoveEvent", self.mouseMoved)

    def mouseMoved(self, *args):
        if self.drag:
            pass
            #print(args[0].GetEventPosition())
    def mouseEntered(self, *args):
        self.drag = False
        print("Entered")

    def mouseLeft(self, *args):
        self.drag = False
        print("Left")

    def leftClick(self, *args):
        if self.drag == False:
            self.drag = True
            self.begin = args[0].GetEventPosition()
            print(self.begin)
            print(self.drag)
        else:
            self.drag = False
            self.end = args[0].GetEventPosition()
            self.drawLine([self.begin, self.end])

    def leftRelease(self, *args):
        self.drag = False
        print(self.drag)


    def initToolbar(self):
        self.actions = Actions(self)

    def drawLine(self, points):
        try:
            self.viewer.GetRenderer().RemoveActor(self.actor)
            self.viewer.GetRenderer().Render()
        except:
            pass
        point1 = points[0]
        point2 = points[1]

        points = vtk.vtkPoints()
        points.SetNumberOfPoints(2)
        points.Allocate(2)

        points.InsertPoint(0, point1[0], point1[1], 0.001)
        points.InsertPoint(1, point2[0], point2[1], 0.001)

        dist = numpy.sqrt(numpy.square((point1[0]-point2[0])*0.028) + numpy.square((point1[1]-point2[1])*0.030))
        self.cells = vtk.vtkCellArray()
        self.cells.Initialize()

        line = vtk.vtkLine()
        line.GetPointIds().SetId(0,0)
        line.GetPointIds().SetId(1,1)
        self.cells.InsertNextCell(line)

        self.poly = vtk.vtkPolyData()
        self.poly.Initialize()
        self.poly.SetPoints(points)
        self.poly.SetLines(self.cells)
        self.poly.Modified()

        mapper = vtk.vtkPolyDataMapper2D()
        #print(dir(mapper))
        mapper.SetInput(self.poly)
        mapper.ScalarVisibilityOn()
        mapper.SetScalarModeToUsePointData()
        mapper.Update()

        self.actor = vtk.vtkActor2D()
        self.actor.SetMapper(mapper)
        self.viewer.GetRenderer().AddActor2D(self.actor)

        box = QtGui.QMessageBox(self)
        box.setInformativeText("Distance: " + str(dist) + " cm.")
        box.show()




    def loadSingleFile(self):
        loader = self.fileLoader
        loader.loadFile()

        if loader.accepted:
            loader.setDir(os.path.dirname(str(loader.selectedFile)))
            self.disableSlider()
            self.dicomReader = vtkgdcm.vtkGDCMImageReader()
            self.dicomReader.SetFileName(str(loader.selectedFile))

            print(dir(self.dicomReader))
            print(self.dicomReader.GetScale())

            self.dicomReader.Update()
            imageData = self.dicomReader.GetOutput()
            size = imageData.GetDimensions()
            width = size[0]
            height = size[1]
            self.vtkWidget.setMaximumSize(QtCore.QSize(width, height))
            self.vtkWidget.setMinimumSize(QtCore.QSize(width, height))

            RefDs = dicom.read_file(str(loader.selectedFile))
            ConstPixelDims = (int(RefDs.Rows), int(RefDs.Columns), 1)

            pointData = imageData.GetPointData()
            arrayData = pointData.GetArray(0)
            arrayDicom = numpy_support.vtk_to_numpy(arrayData)
            arrayDicom = arrayDicom.reshape(ConstPixelDims, order='F')
            shape = arrayDicom.shape
            wtf = arrayDicom.reshape(shape[0], shape[1])
            grad = numpy.gradient(wtf)
            computed = numpy.fliplr(numpy.sqrt(numpy.square(grad[0]) + numpy.square(grad[1]))).transpose()
            self.proc = DrawThread(computed)
            self.proc.start()


            #points = vtk.vtkPoints()
            #points.SetNumberOfPoints(2)
            #points.Allocate(2)

            #points.InsertPoint(0, 100, 100, 0.001)
            #points.InsertPoint(0, 200, 200, 0.001)

            #cells = vtk.vtkCellArray()
            #cells.Initialize()

            #line = vtk.vtkLine()
            #line.GetPointIds().SetId(0,0)
            #line.GetPointIds().SetId(1,1)
            #cells.InsertNextCell(line)

            #poly = vtk.vtkPolyData()
            #poly.Initialize()
            #poly.SetPoints(points)
            #poly.SetLines(cells)
            #poly.Modified()

            #mapper = vtk.vtkPolyDataMapper2D()
            #print(dir(mapper))
            #mapper.SetInput(poly)
            #mapper.ScalarVisibilityOn()
            #mapper.SetScalarModeToUsePointData()
            #mapper.Update()

            #self.drawLine([(200,200), (300,300)])

            #actor = vtk.vtkActor2D()
            #actor.SetMapper(mapper)
            blend = vtk.vtkImageBlend()
            blend.AddInputConnection(self.dicomReader.GetOutputPort())
            #blend.AddInputConnection(actor.GetOutputPort())
            self.viewer.SetInputConnection(blend.GetOutputPort())
            #print(dir(self.viewer.GetRenderer()))
            #self.viewer.GetRenderer().AddActor2D(actor)


            #self.viewer.SetInputConnection(self.dicomReader.GetOutputPort())
            self.viewer.SetZSlice(0)
            self.getMedicalData()
            self.iren.ReInitialize()
            self.iren.Render()
            self.iren.Start()

            #actor = vtk.vtkImageActor()
            #self.viewer.GetRenderer().AddActor(actor)
            self.viewer.GetRenderer().Render()


    def getMedicalData(self):
        #print(self.dicomReader)
        splitter = "Medical Image Properties:"
        data = str(self.dicomReader).split(splitter)
        data = [x.strip() for x in data]
        data = data[1].split('\n')
        data = [x.split(":") for x in data if x]
        self.ui.dicomData.setRowCount(len(data))
        self.ui.dicomData.setColumnCount(1)
        self.ui.dicomData.setHorizontalHeaderItem(0, QtGui.QTableWidgetItem("Data"))
        for i in xrange(0, len(data)):
            self.ui.dicomData.setVerticalHeaderItem(i, QtGui.QTableWidgetItem((data[i][0])))
            self.ui.dicomData.setItem(i, 0, QtGui.QTableWidgetItem((data[i][1])))
        self.ui.dicomData.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.ui.dicomData.setSortingEnabled(False)
        #print(data)

    def disableSlider(self):
        self.ui.playButton.setDisabled(True)
        self.ui.dicomSlider.setDisabled(True)
        self.ui.dicomSlider.setValue(0)
        self.ui.dicomSlider.disconnect(self.ui.dicomSlider, QtCore.SIGNAL("valueChanged(int)"), self.sliderMoved)
        self.ui.playButton.disconnect(self.ui.playButton, QtCore.SIGNAL("clicked()"), self.playMovie)

    @QtCore.pyqtSlot(int)
    def sliderMoved(self, value):
        try:
            self.viewer.SetZSlice(value)
            self.iren.Render()
        except:
            raise ValueError

    @QtCore.pyqtSlot(int)
    def movieStep(self, value):
        self.ui.dicomSlider.setValue(value)
        self.ui.dicomSlider.setSliderDown(value)
        self.viewer.SetZSlice(value)
        self.iren.Render()

    @QtCore.pyqtSlot()
    def playMovie(self):
        self.ui.dicomSlider.disconnect(self.ui.dicomSlider, QtCore.SIGNAL("valueChanged(int)"), self.sliderMoved)
        self.viewer.SetZSlice(0)
        self.obj = Waiter()
        self.obj.trigger.connect(self.movieStep)
        self.obj.ended.connect(self.movieEnded)
        thr = ThreadWait(self.obj, self.ui.dicomSlider.maximum())
        self.queue.put((self.processThread.playMovie, thr, ))

    @QtCore.pyqtSlot()
    def movieEnded(self):
        self.ui.dicomSlider.connect(self.ui.dicomSlider, QtCore.SIGNAL("valueChanged(int)"), self.sliderMoved)

    def enableSlider(self, max):
        self.disableSlider()
        self.ui.playButton.setEnabled(True)
        self.ui.dicomSlider.setTracking(True)
        self.ui.dicomSlider.setEnabled(True)
        self.ui.dicomSlider.setValue(0)
        self.ui.dicomSlider.setMinimum(0)
        self.ui.dicomSlider.setMaximum(max)
        self.ui.dicomSlider.connect(self.ui.dicomSlider, QtCore.SIGNAL("valueChanged(int)"), self.sliderMoved)
        self.ui.playButton.connect(self.ui.playButton, QtCore.SIGNAL("clicked()"), self.playMovie)

    def loadFolder(self):
        loader = self.folderLoader
        loader.loadFile()

        if loader.accepted:
            loader.setDir(os.path.dirname(str(loader.selectedFolder)))
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
            self.vtkWidget.setMaximumSize(QtCore.QSize(width, height))
            self.vtkWidget.setMinimumSize(QtCore.QSize(width, height))
            self.viewer.SetInputConnection(self.dicomReader.GetOutputPort())
            self.iren.ReInitialize()

            self.getMedicalData()

            self.enableSlider(self.seriesSize-1)
            self.ui.dicomSlider.setFocus()

    def undo(self):
        print("Undo")
    def redo(self):
        print("Redo")
    def magnify(self):
        print("Magnify")
    def cut(self):
        print("Cut")

class Actions(object):
    def __init__(self, parent):
        self.parent = parent

        self.loadSingleAction = QtGui.QAction(parent.ui.toolBar)
        self.loadSingleAction.setIcon(QtGui.QIcon(DebugPathBuilder.appendPath(DebugPathBuilder.resourcePath(), "load_one.png")))
        self.loadSingleAction.setToolTip("Load file..")
        parent.ui.toolBar.addAction(self.loadSingleAction)
        self.loadSingleAction.connect(self.loadSingleAction, QtCore.SIGNAL("triggered()"), self.loadSingleFile)

        self.loadFolderAction = QtGui.QAction(parent.ui.toolBar)
        self.loadFolderAction.setIcon(QtGui.QIcon(DebugPathBuilder.appendPath(DebugPathBuilder.resourcePath(), "load_ser.png")))
        self.loadFolderAction.setToolTip("Load series..")
        parent.ui.toolBar.addAction(self.loadFolderAction)
        self.loadFolderAction.connect(self.loadFolderAction, QtCore.SIGNAL("triggered()"), self.loadFolder)

        self.undoAction = QtGui.QAction(parent.ui.toolBar)
        self.undoAction.setIcon(QtGui.QIcon(DebugPathBuilder.appendPath(DebugPathBuilder.resourcePath(), "undo.png")))
        self.undoAction.setToolTip("Undo")
        parent.ui.toolBar.addAction(self.undoAction)
        self.undoAction.connect(self.undoAction, QtCore.SIGNAL("triggered()"), self.undo)

        self.redoAction = QtGui.QAction(parent.ui.toolBar)
        self.redoAction.setIcon(QtGui.QIcon(DebugPathBuilder.appendPath(DebugPathBuilder.resourcePath(), "redo.png")))
        self.redoAction.setToolTip("Redo")
        parent.ui.toolBar.addAction(self.redoAction)
        self.redoAction.connect(self.redoAction, QtCore.SIGNAL("triggered()"), self.redo)

        self.magnifyAction = QtGui.QAction(parent.ui.toolBar)
        self.magnifyAction.setIcon(QtGui.QIcon(DebugPathBuilder.appendPath(DebugPathBuilder.resourcePath(), "magnify.png")))
        self.magnifyAction.setToolTip("Magnify")
        parent.ui.toolBar.addAction(self.magnifyAction)
        self.magnifyAction.connect(self.magnifyAction, QtCore.SIGNAL("triggered()"), self.magnify)

        self.cutAction = QtGui.QAction(parent.ui.toolBar)
        self.cutAction.setIcon(QtGui.QIcon(DebugPathBuilder.appendPath(DebugPathBuilder.resourcePath(), "cut32.png")))
        self.cutAction.setToolTip("Cut")
        parent.ui.toolBar.addAction(self.cutAction)
        self.cutAction.connect(self.cutAction, QtCore.SIGNAL("triggered()"), self.cut)


    def loadSingleFile(self):
        return self.parent.loadSingleFile()

    def loadFolder(self):
        return self.parent.loadFolder()

    def magnify(self):
        return self.parent.magnify()

    def undo(self):
        return self.parent.undo()

    def redo(self):
        return self.parent.redo()

    def cut(self):
        return self.parent.cut()


class Waiter(QtCore.QObject):
    trigger = QtCore.pyqtSignal(int)
    ended = QtCore.pyqtSignal()
    def __init__(self):
        QtCore.QObject.__init__(self)

class ThreadWait(object):
    def __init__(self, obj, length):
        self.obj = obj
        self.length = length
    def threadWait(self):
        for i in xrange(0, self.length + 1):
            time.sleep(0.05)
            self.obj.trigger.emit(i)
        self.obj.ended.emit()

class MyInteractor(QVTKRenderWindowInteractor):
    def __init__(self):
        QVTKRenderWindowInteractor.__init__(self)
        self.AddObserver("LeftButtonPressEvent", self.leftPressed)
        self.Initialize()
        self.Render()
    def leftPressed(self):
        print("WTF")

class DrawThread(threading.Thread):
    def __init__(self, data):
        threading.Thread.__init__(self)
        self.data = data
    def run(self):
        im = plt.imshow(self.data)
        plt.show()

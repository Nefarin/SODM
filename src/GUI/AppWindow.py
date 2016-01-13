### Imports below

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
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import multiprocessing
import scipy
import scipy.interpolate

from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QApplication
from MainWindowGen import Ui_MainWindow
from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from DicomLoader import DicomLoader
from DebugPathBuilder import DebugPathBuilder
from ProcessingThread import ProcessingThread
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar

### End of imports section

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

        #self.figure = plt.figure()
        self.figure, self.axes = plt.subplots(nrows=1, ncols=1)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

        self.figure.subplots_adjust(left=0.00, bottom=0.00, right=1.00, top=1.00)
        #self.im = self.axes.imshow([0.0])
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.ax = self.figure.add_subplot(111)
        self.canvas.updateGeometry()
        plt.axis("off")

        self.firstImage = False
        self.ui.highSlider.setInvertedAppearance(True)
        self.ui.lowSlider.setInvertedAppearance(True)

        #self.vtkWidget = QVTKRenderWindowInteractor(self.ui.imageFrame)
        #self.vtkWidget.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        #self.ui.imageLayout.removeWidget(self.ui.dicomSlider)
        #self.ui.imageLayout.addWidget(self.vtkWidget)
        #self.ui.imageLayout.addWidget(self.ui.dicomSlider)

        self.ui.imageLayout.addWidget(self.canvas)
        self.ui.imageLayout.addWidget(self.toolbar)

        self.disableSlider()
        self.thresholdingOff()

        self.viewer= vtk.vtkImageViewer()
        #self.vtkWidget.GetRenderWindow().AddRenderer(self.viewer.GetRenderer())
        #self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()
        #self.iren.SetRenderWindow(self.vtkWidget.GetRenderWindow())


    def initToolbar(self):
        self.actions = Actions(self)


    def loadSingleFile(self):
        loader = self.fileLoader
        loader.loadFile()

        if loader.accepted:
            loader.setDir(os.path.dirname(str(loader.selectedFile)))
            self.disableSlider()
            self.dicomReader = vtkgdcm.vtkGDCMImageReader()
            self.dicomReader.SetFileName(str(loader.selectedFile))

            self.dicomReader.Update()
            imageData = self.dicomReader.GetOutput()
            size = imageData.GetDimensions()

            RefDs = dicom.read_file(str(loader.selectedFile))

            self.image = self.convertSingleData(imageData, RefDs)
            self.drawSingleData(self.image, 0, self.image.max(), "gray")

            blend = vtk.vtkImageBlend()
            blend.AddInputConnection(self.dicomReader.GetOutputPort())
            self.viewer.SetInputConnection(blend.GetOutputPort())

            self.viewer.SetZSlice(0)
            self.getMedicalData()
            self.thresholdingOn()

    def convertSingleData(self, imageData, RefDs):
        ConstPixelDims = (int(RefDs.Rows), int(RefDs.Columns), 1)
        pointData = imageData.GetPointData()
        arrayData = pointData.GetArray(0)
        arrayDicom = numpy_support.vtk_to_numpy(arrayData)
        arrayDicom = arrayDicom.reshape(ConstPixelDims, order='F')
        shape = arrayDicom.shape
        image = arrayDicom.reshape(shape[0], shape[1])
        image = numpy.fliplr(image).transpose()
        self.min = image.min()
        #print(image.min())
        #print(image.max())
        self.max = image.max()
        #self.max = self.min + 4096
        return image

    def convertMultipleData(self, imagesData, RefDs, seriesSize):
        ConstPixelDims = (int(RefDs.Rows), int(RefDs.Columns), seriesSize)
        pointsData = imagesData.GetPointData()
        arrayData = pointsData.GetArray(0)
        arrayDicom = numpy_support.vtk_to_numpy(arrayData)
        arrayDicom = arrayDicom.reshape(ConstPixelDims, order='F')
        arrayDicom = numpy.swapaxes(arrayDicom, 0, 2)
        images = [numpy.flipud(arrayDicom[i,:,:]) for i in xrange(0, arrayDicom.shape[0])]
        self.min = images[0].min()
        self.max = images[0].max()
        self.image = images[0]
        return images



    def drawSingleData(self, image, min, max, mode):
        image = numpy.clip(image[:], min, max)
        #self.map(image, min, max)
        if not self.firstImage:
            #self.im = self.ax.imshow(image, interpolation="spline36", cmap=plt.get_cmap(mode))
            self.im = self.ax.imshow(image, interpolation="spline36", cmap=plt.get_cmap(mode), vmin = min, vmax = max)
            self.firstImage = True
        else:
            #self.im.set_data(image)
            self.im = self.ax.imshow(image, interpolation="spline36", cmap=plt.get_cmap(mode), vmin = min, vmax = max)
        self.canvas.draw()

    def map(self, image, min, max):
        newImage = numpy.ndarray(image.shape)
        lol = scipy.interpolate.interp1d([image.min(), image.max()], [min, max])
        for i in xrange(0, image.shape[0]):
            for j in xrange(0, image.shape[1]):
                newImage[i][j] = lol(image[i][j])
        return newImage


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
            #self.min = 0;
            #self.max = self.images[value].max()
            self.setMinMax()
            self.drawSingleData(self.images[value], self.min, self.max, "gray")
        except:
            raise ValueError

    @QtCore.pyqtSlot(int)
    def movieStep(self, value):
        self.ui.dicomSlider.setValue(value)
        self.ui.dicomSlider.setSliderDown(value)
        self.drawSingleData(self.images[value], 0, self.images[value].max(), "gray")

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

    def thresholdingOn(self):
        self.ui.highSlider.setEnabled(True)
        self.ui.lowSlider.setEnabled(True)

        self.ui.highSlider.setMinimum(self.min)
        self.ui.highSlider.setMaximum(self.max)

        self.ui.lowSlider.setMinimum(self.min)
        self.ui.lowSlider.setMaximum(self.max)

        self.ui.highSlider.connect(self.ui.highSlider, QtCore.SIGNAL("valueChanged(int)"), self.tChanged)
        self.ui.lowSlider.connect(self.ui.lowSlider, QtCore.SIGNAL(("valueChanged(int)")), self.tChanged)

    def thresholdingOff(self):
        self.ui.highSlider.setDisabled(True)
        self.ui.lowSlider.setDisabled(True)

        self.ui.highSlider.disconnect(self.ui.highSlider, QtCore.SIGNAL("valueChanged(int)"), self.tChanged)
        self.ui.lowSlider.disconnect(self.ui.lowSlider, QtCore.SIGNAL(("valueChanged(int)")), self.tChanged)

    def setMinMax(self):
        self.currentMin = self.ui.lowSlider.value()
        self.currentMax = self.ui.highSlider.value()
        print(self.currentMin)
        print(self.currentMax)

    def tChanged(self):
        self.setMinMax()
        self.drawSingleData(self.image, self.currentMin, self.currentMax, "gray")

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
            rfids = []
            for file in sorted(files):
                temp.SetValue(i, os.path.join(str(loader.selectedFolder), file))
                RefDs = dicom.read_file(str(os.path.join(str(loader.selectedFolder), file)))
                rfids.append(RefDs)
                i = i + 1
            self.dicomReader.SetFileNames(temp)
            self.dicomReader.Update()

            imageData = self.dicomReader.GetOutput()
            size = imageData.GetDimensions()
            width = size[0]
            height = size[1]

            self.viewer.SetInputConnection(self.dicomReader.GetOutputPort())

            self.images = self.convertMultipleData(imageData, rfids[0], self.seriesSize)
            print(len(self.images[0]))
            self.drawSingleData(self.images[0], 0, self.images[0].max(), "gray")
            #for i in xrange(0, self.seriesSize):
            #    self.viewer.SetZSlice(i)
            #    data = self.dicomReader.GetOutput()
            #    #print(dir(data))
            #    #print(rfids[i])
            #    image = self.convertSingleData(data, rfids[i])

            self.getMedicalData()
            self.enableSlider(self.seriesSize-1)
            self.thresholdingOn()
            self.ui.dicomSlider.setFocus()

    def undo(self):
        print("Undo")
    def redo(self):
        print("Redo")
    def magnify(self):
        print("Magnify")
    def cut(self):
        print("Cut")
    def measure(self):
        self.measuring = not self.measuring

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

        self.measureAction = QtGui.QAction(parent.ui.toolBar)
        self.measureAction.setIcon(QtGui.QIcon(DebugPathBuilder.appendPath(DebugPathBuilder.resourcePath(), "line.png")))
        self.measureAction.setToolTip("Measure")
        self.measureAction.setCheckable(True)
        parent.ui.toolBar.addAction(self.measureAction)
        self. measureAction.connect(self.measureAction, QtCore.SIGNAL("triggered()"), self.measure)



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

    def measure(self):
        return self.parent.measure()


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


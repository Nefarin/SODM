from PyQt4 import QtGui, QtCore
from DebugPathBuilder import DebugPathBuilder

class DicomLoader(QtCore.QObject):
    def __init__(self, parent, mode):
        QtGui.QFileDialog.__init__(parent)
        self.parent = parent
        if mode == "file":
            self.mode = mode

            self.filter = "File Description (*.dcm)"
            self.prompt = "Select a dicom file.."
            self.dialog = QtGui.QFileDialog(self.parent)

            self.initBasic()
            self.initConnections()

        elif mode == "series":
            self.mode = mode

            self.filter = "Folder Description (*.dcm)"
            self.prompt = "Select a dicom folder.."
            self.dialog = QtGui.QFileDialog(self.parent)

            self.dialog.setFileMode(QtGui.QFileDialog.Directory)
            self.dialog.setOption(QtGui.QFileDialog.ShowDirsOnly, False)
            #self.dialog.setOption(QtGui.QFileDialog.ShowDirsOnly, True)

            self.initBasic()
            self.initConnections()
        else:
            raise Exception("Invalid mode")

    def initBasic(self):

        self.accepted = False
        self.dialog.setModal(True)
        self.dialog.setFilter(self.filter)
        self.dialog.setDirectory(DebugPathBuilder.resourcePath())
        self.dialog.setWindowTitle(self.prompt)

    def initConnections(self):

        self.dialog.connect(self.dialog, QtCore.SIGNAL("accepted()"), self.accept)
        self.dialog.connect(self.dialog, QtCore.SIGNAL("rejected()"), self.reject)
        self.dialog.connect(self.dialog, QtCore.SIGNAL("finished()"), self.finish)


    def loadFile(self):
        self.dialog.exec_()

    def setDir(self, directory):
        self.dialog.setDirectory(directory)

    def accept(self):

        self.accepted = True

        if self.mode == "file":
            self.selectedFile = self.dialog.selectedFiles()[0]

        elif self.mode == "series":
            self.selectedFolder = self.dialog.selectedFiles()[0]
        else:
            raise Exception("Invalid mode")

    def reject(self):
        self.accepted = False

    def finish(self):
        self.accepted = False

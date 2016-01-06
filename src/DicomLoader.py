from PyQt4 import QtGui, QtCore
from DebugPathBuilder import DebugPathBuilder

class DicomLoader(QtCore.QObject):
    def __init__(self, parent):
        QtGui.QFileDialog.__init__(parent)
        self.parent = parent
        self.filter = "File Description (*.dcm)"
        self.prompt = "Select a dicom file.."
        self.dialog = QtGui.QFileDialog(self.parent)

        self.accepted = False

        self.dialog.setModal(True)
        self.dialog.setFilter(self.filter)
        self.dialog.setDirectory(DebugPathBuilder.resourcePath())
        self.dialog.setWindowTitle(self.prompt)

        self.dialog.connect(self.dialog, QtCore.SIGNAL("accepted()"), self.accept)
        self.dialog.connect(self.dialog, QtCore.SIGNAL("rejected()"), self.reject)
        self.dialog.connect(self.dialog, QtCore.SIGNAL("finished()"), self.finish)

    def loadFile(self):
        self.dialog.exec_()

    def accept(self):
        self.accepted = True
        self.selectedFile = self.dialog.selectedFiles()[0]

    def reject(self):
        self.accepted = False

    def finish(self):
        self.accepted = False

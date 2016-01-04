import sys
import imp
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QApplication
from MainWindowGen import Ui_MainWindow

class AppWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self);
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.toolBar.addAction(QtGui.QAction("wtf", self.ui.toolBar))



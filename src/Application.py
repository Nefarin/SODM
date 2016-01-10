import sys
import imp
import os
import setup
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QApplication
import AppWindow as m

class Application():
    def __init__(self):
        pass
    def run(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Simple Dicom Viewer")
        self.window = m.AppWindow(self.app)
        self.app.connect(self.app, QtCore.SIGNAL("aboutToQuit()"), self.exit)
        self.window.show()
        #window.iren.Initialize()
        return sys.exit(self.app.exec_())

    def exit(self):
        self.window.queue.put((self.window.processThread.stop, None,))
        self.app.exit()

if __name__ == '__main__':
    app = Application()
    app.run()
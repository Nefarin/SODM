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
        window = m.AppWindow()
        window.show()
        return sys.exit(self.app.exec_())

if __name__ == '__main__':
    app = Application()
    app.run()
#!/usr/bin/env python

import os
import sys

from PyQt4 import QtCore, QtGui

from ui import qtracker

class QTrackerMW(QtGui.QMainWindow):
    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self,
                                           'Message',
                                           "Are you sure to quit?",
                                           QtGui.QMessageBox.Yes,
                                           QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

class QTracker(QtCore.QObject):
    def __init__(self):
        QtCore.QObject.__init__(self)
        self.mw = QTrackerMW()
        self.ui = qtracker.Ui_MainWindow()
        self.ui.setupUi(self.mw)
        self.mw.show()

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    main = QTracker()
    app.connect(app, QtCore.SIGNAL('close()'), app.exit)
    sys.exit(app.exec_())

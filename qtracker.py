#!/usr/bin/env python

import os
import sys
import sqlite3

from PyQt4 import QtCore, QtGui

from ui import qtracker, project
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from models import Project, Task, Slot, Base

from sqlalchemy.ext.declarative import declarative_base


class QTrackerMW(QtGui.QMainWindow):
    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self,
                                           'Exit',
                                           "Are you sure to quit?",
                                           QtGui.QMessageBox.Yes,
                                           QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

class QTracker(QtCore.QObject):
    db_path = os.path.expanduser('~/.config/qtracker/db.sqlite3')

    def __init__(self):
        QtCore.QObject.__init__(self)
        self.mw = QTrackerMW()
        self.ui = qtracker.Ui_MainWindow()
        self.ui.setupUi(self.mw)
        self.mw.show()
        self.pw = QtGui.QWidget()
        self.pui = project.Ui_widget()
        self.pui.setupUi(self.pw)
        
        #print "DB path => %s" % self.db_path
        self.engine = create_engine('sqlite:///%s' % self.db_path, echo=True)
        self.session = sessionmaker(bind = self.engine)
        self.meta = Base.metadata
        self.meta.create_all(self.engine)

        QtCore.QObject.connect(self.ui.addproject_button, QtCore.SIGNAL('clicked()'), self.pw.show)
        QtCore.QObject.connect(self.pui.button_box, QtCore.SIGNAL('accepted()'), self.add_project)


    def add_project(self):
        name = self.pui.newproject_line.text()
        p = Project(name)
        #p.name = self.pui.newproject_line.text()
        print "Devo creare il progetto =>", self.pui.newproject_line.text()
        self.session.add(p)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    main = QTracker()
    app.connect(app, QtCore.SIGNAL('close()'), app.exit)
    sys.exit(app.exec_())

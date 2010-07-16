#!/usr/bin/env python

import os
import sys
import sqlite3

from PyQt4 import QtCore, QtGui

from ui import qtracker, project, task
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from models import Project, Task, Slot, Base

from sqlalchemy.ext.declarative import declarative_base

HOUR = 60 * 60
MINUTE = 60

def htime(seconds):
    h = seconds / HOUR
    m = (seconds - h * HOUR) / MINUTE
    s = seconds % MINUTE
    return "%d:%02d:%02d" % (h, m, s) if h > 0 else "%02d:%02d" % (m, s)

class QTrackerMW(QtGui.QMainWindow):
    close_signal = QtCore.pyqtSignal()

    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self,
                                           'Exit',
                                           "Are you sure to quit?",
                                           QtGui.QMessageBox.Yes,
                                           QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            self.close_signal.emit()
            event.accept()
        else:
            event.ignore()

class QTracker(QtCore.QObject):
    db_path = os.path.expanduser('~/.config/qtracker/db.sqlite3')
    current_slot = False
    cp = None
    ct = None

    def __init__(self):
        QtCore.QObject.__init__(self)
        self.mw = QTrackerMW()
        self.ui = qtracker.Ui_QTracker()
        self.ui.setupUi(self.mw)

        self.pw = QtGui.QWidget()
        self.pui = project.Ui_widget()
        self.pui.setupUi(self.pw)

        self.tw = QtGui.QWidget()
        self.tui = task.Ui_widget()
        self.tui.setupUi(self.tw)
        #print "DB path => %s" % self.db_path
        self.engine = create_engine('sqlite:///%s' % self.db_path, echo=False)
        self._session = sessionmaker(bind = self.engine)
        self.meta = Base.metadata
        self.meta.create_all(self.engine)
        self.session = self._session()
        QtCore.QObject.connect(self.ui.addproject_button, QtCore.SIGNAL('clicked()'), self.pw.show)
        QtCore.QObject.connect(self.ui.addtask_button, QtCore.SIGNAL('clicked()'), self.tw.show)
        QtCore.QObject.connect(self.pui.button_box, QtCore.SIGNAL('accepted()'), self.add_project)
        QtCore.QObject.connect(self.tui.button_box, QtCore.SIGNAL('accepted()'), self.add_task)
        QtCore.QObject.connect(self.ui.project_combo, QtCore.SIGNAL('activated(int)'), self.choose_project)
        QtCore.QObject.connect(self.ui.start_button, QtCore.SIGNAL('clicked()'), self.start_slot)
        QtCore.QObject.connect(self.ui.stop_button, QtCore.SIGNAL('clicked()'), self.stop_slot)
        QtCore.QObject.connect(self.ui.rebuild, QtCore.SIGNAL('clicked()'), self.build)
        self.mw.close_signal.connect(self.stop_slot)
        self.build()
        self.build_tray_menu()
        self.choose_project(self.ui.project_combo.currentIndex())
        self.mw.show()

    def build_tray_menu(self):
        tr = QtGui.QIcon()
        tr.addPixmap(QtGui.QPixmap(":/icons/foto.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.tray = QtGui.QSystemTrayIcon(tr, self)
        self.tray.show()
        self.traymenu = QtGui.QMenu("QTracker Tray Menu")
        self.tm_switch = QtGui.QAction(self.mw)
        self.tm_switch.setText("&Switch to")
        self.traymenu.addAction(self.tm_switch)
        #self.about_widget.connect(self.tm_about, QtCore.SIGNAL('triggered()'), QtCore.SLOT('show()'))
        for i in self.projects:
            a = QtGui.QAction(self.mw)
            a.setText(i.name)
            self.traymenu.addAction(a)


        # self.tm_about = QAction(self.mw)
        # self.tm_about.setText(QApplication.translate("MainWindow", "&About", None, QApplication.UnicodeUTF8))
        # self.about_widget.connect(self.tm_about, QtCore.SIGNAL('triggered()'), QtCore.SLOT('show()'))

        # self.tm_close = QAction(self.mw)
        # self.tm_close.setText(QApplication.translate("MainWindow", "&Close", None, QApplication.UnicodeUTF8))
        # self.mw.connect(self.tm_close, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()'))

        # self.traymenu.addAction(self.tm_about)
        # self.traymenu.addAction(self.tm_close)
        QtCore.QObject.connect(self.tray, QtCore.SIGNAL('activated(QSystemTrayIcon::ActivationReason)'), self.show_main)
        self.tray.setContextMenu(self.traymenu)

    @QtCore.pyqtSlot(int)
    def show_main(self, value = -3):
        if value in [2, 3]:
            if self.mw.isVisible():
                self.mw.hide()
            else:
                self.mw.show()


    def current_project_task(self):
        _p = _t = None
        if self.ui.project_combo.currentIndex() >= 0:
            _p = self.projects[self.ui.project_combo.currentIndex()]
            if self.ui.task_combo.currentIndex() >= 0:
                _t = _p.tasks[self.ui.task_combo.currentIndex()]
        return _p, _t


    def start_slot(self):
        if self.current_slot:
            self.stop_slot()
        project, task = self.current_project_task()
        self.current_slot = Slot(project, task)
        self.session.add(self.current_slot)
        self.session.commit()
        self.ui.stop_button.setEnabled(True)
        self.ui.start_button.setEnabled(False)

    def stop_slot(self):
        if not self.current_slot:
            return
        self.current_slot.stop()
        time_for_slot = self.current_slot.end - self.current_slot.start
        p = self.current_slot.project
        p.time_spent += time_for_slot.seconds
        t = self.current_slot.task
        if t:
            t.time_spent += time_for_slot.seconds
            self.session.add(t)
        self.session.add(p)
        self.session.add(self.current_slot)
        self.session.commit()
        self.ui.stop_button.setEnabled(False)
        self.ui.start_button.setEnabled(True)
        self.current_slot = False
        #self.build()


    def build(self, project = None, task = None):
        _p = _t = None
        if project:
            _p = project
        else:
            if self.ui.project_combo.currentIndex() >= 0:
                _p = self.projects[self.ui.project_combo.currentIndex()]
        if task:
            _t = task
        # else:
        #     if self.ui.task_combo.currentIndex() >= 0:
        #         _t = _p.tasks[self.ui.task_combo.currentIndex()]

        print "P T", _p, _t
        self.tui.project_combo.clear()
        self.ui.project_combo.clear()
        self.ui.time_report.clear()
        self.projects = self.session.query(Project).order_by('name').all()
        for p in self.projects:
            print "Tasks for %s =>" % p, p.tasks
            self.tui.project_combo.addItem(p.name)
            self.ui.project_combo.addItem(p.name)
            parent = QtGui.QTreeWidgetItem(self.ui.time_report, [p.name, htime(p.time_spent), str(len(p.slots))])
            parent.setExpanded(True)
            for t in p.tasks:
                parent.addChild(QtGui.QTreeWidgetItem([t.name, htime(t.time_spent), str(len(t.slots))]))
        if _p:
            self.choose_project(self.projects.index(_p))
            if _t:
                self.ui.task_combo.setCurrentIndex(_p.tasks.index(_t))
        

    def add_project(self):
        name = str(self.pui.newproject_line.text())
        print "Devo creare il progetto =>", name
        exists = self.session.query(Project).filter_by(name = name).all()
        if exists:
            self.pui.error.setText("Project %s already exixts!" % name)
            return
        self.pui.error.setText("")
        p = Project(name)
        self.session.add(p)
        self.session.commit()
        print p.id
        self.pw.hide()
        self.pui.newproject_line.setText('')
        self.build(project)

    def add_task(self):
        name = str(self.tui.newtask_line.text())
        p = self.tui.project_combo.currentIndex()
        project = self.projects[p]
        print "Adding task %s for project %s" % (name, p)
        exists = self.session.query(Task).filter_by(name = name, project = project).all()
        if exists:
            self.tui.error.setText("Task %s for project %s already exists!" % (name, project.name))
            return

        self.tui.error.setText("")
        t = Task(name, project)
        self.session.add(t)
        self.session.commit()
        self.tw.hide()
        self.tui.newtask_line.setText('')
        self.build(project, t)

    def choose_project(self, index, task = None):
        if index < 0:
            self.ui.task_combo.clear()
            return
        self.tui.project_combo.setCurrentIndex(index)
        self.ui.task_combo.clear()
        for t in self.projects[index].tasks:
            self.ui.task_combo.addItem(t.name)
        if task:
            self.ui.task_combo.setIndex(task)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    main = QTracker()
    app.connect(app, QtCore.SIGNAL('close()'), app.exit)
    sys.exit(app.exec_())

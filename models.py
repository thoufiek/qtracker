#!/usr/bin/env python
        
import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

from sqlalchemy import Table, Column, Integer, String, DateTime

Base = declarative_base()

class Project(Base):
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key = True)
    name = Column(String)
    time_spent = Column(Integer)

    created = Column(DateTime)
    modified = Column(DateTime)

    def __init__(self, name):
        self.name = name
        self.created = datetime.datetime.now()
        self.modified = datetime.datetime.now()
        self.time_spent = 0

    def __repr__(self):
        return "<Project %s :: %d:%02d spent>" % (self.name, self.time_spent/60, self.time_spent%60)

class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key = True)
    name = Column(String)
    time_spent = Column(Integer)

    created = Column(DateTime)
    modified = Column(DateTime)
    project = relationship(Project, backref = backref('tasks', order_by = created))
    def __init__(self, name, project):
        self.name = name
        self.time_spent = 0
        self.created = datetime.datetime.now()
        self.modified = datetime.datetime.now()
        self.project = project

    def __repr__(self):
        return "<Task %s from project %s :: %d:%02d spent>" % (self.name, self.project.name, self.time_spent/60, self.time_spent%60)

class Slot(Base):
    __tablename__ = 'slots'

    id = Column(Integer, primary_key = True)
    start = Column(DateTime)
    end = Column(DateTime)
    created = Column(DateTime)
    modified = Column(DateTime)
    project = relationship(Project)
    task = relationship(Task)

    def __init__(self, project, task = None):
        self.project = project
        self.task = task
        self.created = datetime.datetime.now()
        self.modified = datetime.datetime.now()
        self.start = datetime.datetime.now()
        self.end = None


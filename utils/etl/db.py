#coding=utf-8
'''
Created on Jan 9, 2017

@author: Felix
'''

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import ForeignKey
from sqlalchemy import Column, \
                       Integer, \
                       String, \
                       DateTime, \
                       SmallInteger, \
                       Text

Base = declarative_base()

class DB(object):
    def __init__(self, engine=None):
        if engine:
            self._engine = engine
        else:
            self._engine = create_engine('sqlite://///opt/www/matrix-pixel/matrix-pixel/db.sqlite3', echo=True)
        _Session = sessionmaker(bind=self._engine)
        self._session = _Session()
        
    def get_computation_engine_settings(self):
        return self._session.query(ETLComputeEngine).all()
    
    def get_storage_engine_settings(self):
        return self._session.query(ETLStorageEngine).all()
    
    def get_computation_settings(self):
        return self._session.query(ETLDatawarehouseComputationConfiguration).all()
    
    def get_report_unit_settings(self):
        return self._session.query(ETLReportUnit).all()

class ETLComputeEngine(Base):
    __tablename__ = 'etl_computeengine'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    desc = Column(Text)
    conf = Column(Text)
    date_added = Column(DateTime)
    date_updated = Column(DateTime)
    ctype = Column(String(32))

    def __repr__(self):
        return '<ETLComputeEngine(id={!r}, name={!r}, ctype={!r})>'.format(self.id, 
                                                                           self.name, 
                                                                           self.ctype)

class ETLStorageEngine(Base):
    __tablename__ = 'etl_storageenigne'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    desc = Column(Text)
    stype = Column(String(32))
    setype = Column(String(32))
    conf = Column(Text)
    date_added = Column(DateTime)
    date_updated = Column(DateTime)
    
    def __repr__(self):
        return 'ETLStorageEngine(id={!r}, name={!r}, stype={!r}, setype={!r})'.format(self.id, 
                                                                         self.name,
                                                                         self.stype,
                                                                         self.setype)

class ETLDatawarehouseComputationConfiguration(Base):
    __tablename__ = 'etl_datawarehousecomputeconfiguration'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    desc = Column(Text)
    template = Column(Text)
    engine_id = Column(Integer, ForeignKey('etl_computeengine.id'))
    output = Column(Text) # output to the dynamic context storage
    layer = Column(SmallInteger)
    date_added = Column(DateTime)
    date_updated = Column(DateTime)
    
    def __repr__(self):
        return 'ETLDatawarehouseComputationConfiguration(id={!r}, name={!r}, engine_id={!r})'.format(self.id, 
                                                                                                 self.name,
                                                                                                 self.engine_id) 
class ETLReportUnit(Base):
    __tablename__ = 'etl_reportunit'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    refer = Column(String(128))
    dimension = Column(Text)
    desc = Column(Text)
    template = Column(Text)
    output = Column(Text) # output to final result storage
    visualization = Column(Text)
    date_added = Column(DateTime)
    date_updated = Column(DateTime)
    engine_id = Column(Integer, ForeignKey('etl_computeengine.id'))
    
    def __repr__(self):
        return 'ETLReportUnit(id={!r}, name={!r}, engine_id={!r})'.format(self.id, 
                                                                          self.name,
                                                                          self.engine_id)                             

if __name__ == '__main__':
    engine = create_engine('sqlite:////Users/Felix/Documents/workspace/matrix-pixel/db.sqlite3', echo=True)
    Session = sessionmaker(bind=engine)
    
#     DB.Base.metadata.create_all(engine)
    session = Session()
    my_e = session.query(ETLReportUnit).all()
    print(my_e)

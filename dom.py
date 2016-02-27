from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

db = create_engine('mysql://root:root@localhost/torinomusei?charset=utf8', echo=True)
Base = declarative_base()

class Museo(Base):
    __tablename__ = 'musei'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    
    def __init__(self, name):
        self.name = name

class Collezione(Base):
    __tablename__ = 'collezioni'
    
    id = Column(Integer, primary_key=True)
    titolo = Column(String(255))
    autore = Column(String(255))
    datazione = Column(String(255))
    tecnica = Column(String(255))
    dimensioni = Column(String(255))
    immagine = Column(String(255))
    
    museo_id = Column(Integer, ForeignKey("musei.id"))
    museo = relationship("Museo", backref=backref("collezione", order_by=id))
    
    def __init__(self, titolo, autore, datazione, tecnica, dimensioni, immagine):
        self.titolo = titolo
        self.autore = autore
        self.datazione = datazione
        self.tecnica = tecnica
        self.dimensioni = dimensioni
        self.immagine = immagine

Base.metadata.create_all(db)
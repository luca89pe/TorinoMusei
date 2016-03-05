from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Date
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
    
    def serialize(self):
        return {
                'id':self.id,
                'titolo':self.titolo,
                'autore':self.autore,
                'datazione':self.datazione,
                'tecnica':self.tecnica,
                'dimensioni':self.dimensioni,
                'immagine':self.immagine,
                'museo_id':self.museo_id
                }
    
    def __init__(self, titolo, autore, datazione, tecnica, dimensioni, immagine):
        self.titolo = titolo
        self.autore = autore
        self.datazione = datazione
        self.tecnica = tecnica
        self.dimensioni = dimensioni
        self.immagine = immagine
        
class Affluenza(Base):
    __tablename__ = 'affluenza'
    
    id = Column(Integer, primary_key=True)
    data = Column(Date)
    intero = Column(Integer)
    ridotto = Column(Integer)
    omaggio = Column(Integer)
    abbonamento = Column(Integer)
    scuole = Column(Integer)
    
    museo_id = Column(Integer, ForeignKey("musei.id"))
    museo = relationship("Museo", backref=backref("affluenza", order_by=id))
    
    def __init__(self, data, intero, ridotto, omaggio, abbonamento, scuole):
        self.data = data
        self.intero = intero
        self.ridotto = ridotto
        self.omaggio = omaggio
        self.abbonamento = abbonamento
        self.scuole = scuole

class Utente(Base):
    __tablename__ = 'utenti'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(32))
    password = Column(String(255))

class Token(Base):
    __tablename__ = 'tokens'
    
    utente = Column(Integer, ForeignKey("utenti.id"))
    token = Column(String(32), primary_key=True)
    
    def __init__(self, utente, token):
        self.utente = utente
        self.token = token

class Preferiti(Base):
    __tablename__ = 'preferiti'
    
    id = Column(Integer, primary_key=True)
    utente_id = Column(Integer, ForeignKey("utenti.id"))
    collezione_id = Column(Integer, ForeignKey("collezioni.id"))
    
    def __init__(self, utente_id, collezione_id):
        self.utente_id = utente_id
        self.collezione_id = collezione_id

def createDB():
    Base.metadata.create_all(db)
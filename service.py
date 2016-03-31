from sqlalchemy import create_engine, text
from dom import Museo, Collezione, Utente, Token, Preferiti
from sqlalchemy.orm.session import sessionmaker
import pandas as pd
import uuid
from flask.json import jsonify
import time

db = create_engine('mysql://root:root@localhost/torinomusei?charset=utf8')
Session = sessionmaker(bind=db, autocommit=True)
session = Session()


def FindAllMusei():
    q = text('SELECT * FROM musei LIMIT 3')
    return db.execute(q).fetchall()

def FindMuseo(museo):
    query = text('SELECT * FROM musei WHERE id = :museo')
    query = query.bindparams(museo = museo)
    return db.execute(query).fetchone()

def FindCollezioniMuseo(museo_id, start, step):
    print "start: ", start, " - step: ", step
    start = int(start)
    step = int(step)
    query=text('SELECT * FROM collezioni WHERE museo_id=:museo_id')
    query=query.bindparams(museo_id=museo_id)
    res = db.execute(query).fetchall()
    return res[start:(start+step)]

def FindCollezione(museo, collezione):
    q = text('SELECT * FROM collezioni WHERE id=:collezione AND museo_id=:museo')
    q = q.bindparams(collezione=collezione, museo=museo)
    result = db.execute(q)
    return result.fetchone()

def AffluenzaByWeekDay(museo):
    # Query sql fatta direttamente con pandas
    df = pd.read_sql_table('affluenza', db, parse_dates=['data'])
    df = df.drop('id', 1)
    df = df[df['museo_id'] == museo]    # Seleziono solo i record del museo scelto
    df = df.drop('museo_id', 1)
    df['weekday'] = df['data'].dt.dayofweek     # Aggiungo i giorni della settimana
    dfbyday = df.groupby('weekday').sum()
    return (dfbyday.sum(axis=1)).to_json()

def MediaAffluenzaByWeekDay(museo):
    # Query sql fatta direttamente con pandas
    df = pd.read_sql_table('affluenza', db, parse_dates=['data'])
    df = df.drop('id', 1)   # 1 indica l'asse (ossia elimina la colonna, e non la riga
    df = df[df['museo_id'] == museo]
    df = df.drop('museo_id', 1)
    df['weekday'] = df['data'].dt.dayofweek
    media = df.groupby('weekday').mean().sum(axis=1).round(2)
    return media

def isUserInDb(username):
    q = text('SELECT * FROM utenti WHERE username = :username')
    q = q.bindparams(username = username)
    res = db.execute(q).fetchone()
    if res is not None:
        return True
    else:
        return False

def signup(username, password):
    if isUserInDb(username):
        return 'exists'
    utente = Utente(username, password)
    session.add(utente)
    session.commit()
    time.sleep(0.5)
    res = session.query(Utente).filter(Utente.username == username).first()
    print 'return signup ', res
    if res is None:
        return 'ko'
    return res

def auth(username, password):
    q = text('SELECT username FROM utenti WHERE username=:username AND password=:password')
    q = q.bindparams(username=username, password=password)
    user = db.execute(q).fetchone()
    if user is not None:
        print "I dati di accesso sono corretti"
    else:
        print "I dati di accesso non sono corretti"
    return user
    
def generateToken(username, password):
    # Check if username and password are correct, if none returns "wrong"
    if auth(username, password) is None:
        return 'wrong'
    # Username and password are right, so check if the user has an associated token
    utente_id = session.query(Utente).filter(Utente.username==username).first()
    utente_id = utente_id.id
    q = text('SELECT token FROM tokens WHERE utente=:utente_id')
    q = q.bindparams(utente_id=utente_id)
    token = db.execute(q).fetchone()
    print token
    # If there is a token for that user, returns the token
    if token is not None:
        return token
    # If there isn't token for the user, try to generate one
    while True:
        token = uuid.uuid4().hex
        print token
        res = session.query(Token).filter(Token.token == token).first()
        if res is not None:
            print "esiste gia il token ", token, " nella tabella"
        if res is None:
            print "Il token non esiste, quindi lo restituisco al chiamante"
            break
    q = text('INSERT INTO tokens VALUES (:utente_id, :token)')
    q = q.bindparams(utente_id=utente_id, token=token)
    db.execute(q)
    d = {'token': token}
    return d


def deleteToken(token):
    q= text('SELECT token FROM tokens WHERE token=:token')
    q=q.bindparams(token=token)
    res=db.execute(q).fetchone()
    if res is None:
        return 'token inesistente'
    q=text('DELETE FROM tokens WHERE token=:token' ) 
    q=q.bindparams(token=token)
    res=db.execute(q)

def ricerca(query, searchType, start):
    print query, " - ", searchType, " - ", start
    step = 30
    start = int(start)
    res = session.query(Collezione).filter(getattr(Collezione, searchType).ilike("%"+query+"%")).all()
    print res, "type: ",type(res)
    return res[start:(start+step)]

# Verifico che il token sia associato a qualche utente. In caso positivo, ritorno l'id dell'utente
def checkToken(token):
    print 'service.checkToken: ',token
    q = text('SELECT * FROM tokens WHERE token=:token')
    q = q.bindparams(token=token)
    res = db.execute(q).fetchone()
    print "cerca token: ",res
    if res is None:
        return None
    return res.utente

# Verifico che la collezione esista nel db
def checkCollezione(collezione_id):
    res = session.query(Collezione).filter(Collezione.id == collezione_id).one_or_none()
    if res is None:
        return None
    return res.id

def addPreferito(utente_id, collezione_id):
    q = text('SELECT * FROM preferiti WHERE utente_id = :utente_id AND collezione_id = :collezione_id')
    q = q.bindparams(utente_id=utente_id, collezione_id=collezione_id)
    res = db.execute(q).fetchone()
#     res = session.query(Preferiti).filter(Preferiti.utente_id == utente_id, Preferiti.collezione_id == collezione_id).one_or_none()
    if res is not None:
        return 'exists'
    q = text('INSERT INTO preferiti(utente_id, collezione_id) VALUES(:utente_id, :collezione_id)')
    q = q.bindparams(utente_id=utente_id, collezione_id=collezione_id)
    db.execute(q)
#     preferito = Preferiti(utente_id, collezione_id)
#     session.add(preferito)
#     session.commit()

def findPreferiti(utente_id):
    print "findPreferiti - utente_id: ", utente_id
    preferiti = session.query(Preferiti).filter(Preferiti.utente_id == utente_id).all()
    if preferiti is None:
        return None
    preferiti_id = []
    for p in preferiti:
        preferiti_id.append(p.collezione_id)
#     preferiti_id = preferiti.id.tolist()
    print "preferiti_id: ", preferiti_id
#     collezioni = session.query(Collezione).filter(Collezione.id.in_(row.collezione_id for row in preferiti)).all()
    collezioni = session.query(Collezione).filter(Collezione.id.in_(preferiti_id)).all()
    return collezioni

def deletePreferito(utente_id, collezione_id):
    session.query(Preferiti).filter(Preferiti.utente_id == utente_id, Preferiti.collezione_id == collezione_id).delete()
    session.commit()

def changePassword(utente_id, password, newpassword):
    utente = session.query(Utente).filter(Utente.id == utente_id, Utente.password == password).one_or_none()
    if utente is None:
        return 'password errata'
    session.query(Utente).filter(Utente.id == utente_id).update({Utente.password : newpassword})
    session.commit()

def deleteAccount(utente_id):
    session.query(Utente).filter(Utente.id == utente_id).delete()
    session.commit()

def getUtenteFromId(utente_id):
    return session.query(Utente).filter(Utente.id == utente_id).one_or_none()
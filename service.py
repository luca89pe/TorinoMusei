from sqlalchemy import create_engine, text
from dom import Museo, Collezione, Utente, Token, Preferiti
from sqlalchemy.orm.session import sessionmaker
import pandas as pd
import uuid
from flask.json import jsonify

db = create_engine('mysql://root:root@localhost/torinomusei?charset=utf8')
Session = sessionmaker(bind=db)
session = Session()


def FindAllMusei():
    query = text('SELECT * FROM musei')
    results = db.execute(query)
    return results.fetchall()

def FindMuseo(museo):
    query = text('SELECT * FROM musei WHERE id = :museo')
    query = query.bindparams(museo = museo)
    return db.execute(query).fetchone()

def FindCollezioniMuseo(museo_id):
    query=text('SELECT * FROM collezioni WHERE museo_id=:museo_id LIMIT 20')
    query=query.bindparams(museo_id=museo_id)
    return (db.execute(query)).fetchall()

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

def AffluenzaByWeekDayPlot(museo):
    # Query sql fatta direttamente con pandas
    df = pd.read_sql_table('affluenza', db, parse_dates=['data'])
    df = df.drop('id', 1)
    df = df[df['museo_id'] == museo]
    df = df.drop('museo_id', 1)
    df['weekday'] = df['data'].dt.dayofweek
    dfbyday = df.groupby('weekday').sum()
    return dfbyday.sum(axis=1)

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
    else:
        q = text('INSERT INTO utenti(username, password) VALUES (:username, :password)')
        q = q.bindparams(username=username, password=password)
        db.execute(q)

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
    utente_id = session.query(Utente).filter(Utente.username==username).one().id
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

def ricerca(query):
    res = session.query(Collezione).filter((Collezione.titolo.ilike('%'+query+'%')) | (Collezione.autore.ilike('%'+query+'%')) | (Collezione.tecnica.ilike('%'+query+'%'))).all()
    print res, "type: ",type(res)
    return res

# Verifico che il token sia associato a qualche utente. In caso positivo, ritorno l'id dell'utente
def checkToken(token):
    res = session.query(Token).filter(Token.token == token).one_or_none()
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
    res = session.query(Preferiti).filter(Preferiti.utente_id == utente_id, Preferiti.collezione_id == collezione_id).one_or_none()
    if res is not None:
        return 'exists'
    preferito = Preferiti(utente_id, collezione_id)
    session.add(preferito)
    session.commit()

def findPreferiti(utente_id):
    preferiti = session.query(Preferiti).filter(Preferiti.utente_id == utente_id).all()
    if preferiti is None:
        return None
    collezioni = session.query(Collezione).filter(Collezione.id.in_(row.id for row in preferiti)).all()
    return collezioni

def deletePreferito(utente_id, collezione_id):
    session.query(Preferiti).filter(Preferiti.utente_id == utente_id, Preferiti.collezione_id == collezione_id).delete()
    session.commit()
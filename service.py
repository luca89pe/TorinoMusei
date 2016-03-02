from sqlalchemy import create_engine, text
from dom import Museo, Collezione, Utente, Token
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
    query=text('SELECT * FROM collezioni WHERE museo_id=:museo_id')
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

def generateToken(username, password):
    q = text('SELECT username FROM utenti WHERE username=:username AND password=:password')
    q = q.bindparams(username=username, password=password)
    res = db.execute(q).fetchone()
    if res is None:
        return None
    utente_id = session.query(Utente).filter(Utente.username==username).one().id
    q = text('SELECT token FROM tokens WHERE utente=:utente_id')
    q = q.bindparams(utente_id=utente_id)
    res = db.execute(q).fetchone()
    print res
    if res is not None:
        return res
#     token = uuid.uuid4().hex
    token = "ciaone"
    res = session.query(Token).filter(Token.token == token).one().token
    if res is not None:
        print "token gia presente: ", res
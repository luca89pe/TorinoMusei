from sqlalchemy import create_engine, text
from dom import Museo, Collezione
from sqlalchemy.orm.session import sessionmaker
import pandas as pd

db = create_engine('mysql://root:root@localhost/torinomusei?charset=utf8')
Session = sessionmaker(bind=db)
session = Session()


def FindAllMusei():
    query = text('SELECT * FROM musei')
    results = db.execute(query)
    return results.fetchall()

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
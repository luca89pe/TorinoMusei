from sqlalchemy import create_engine, text
from dom import Museo, Collezione
from sqlalchemy.orm.session import sessionmaker
import pandas as pd

db = create_engine('mysql://root:root@localhost/torinomusei?charset=utf8')
Session = sessionmaker(bind=db)
session = Session()


def FindAllMusei():
    query = text('SELECT * FROM musei')
    return (db.execute(query)).fetchall()

def FindCollezioniMuseo(museo_id):
    query=text('SELECT * FROM collezioni WHERE museo_id=:museo_id')
    query=query.bindparams(museo_id=museo_id)
    return (db.execute(query)).fetchall()

def FindCollezione(collezione):
    q = text('SELECT * FROM collezioni WHERE id=:collezione')
    q = q.bindparams(collezione=collezione)
    return (db.execute(q)).fetchone()

def AffluenzaByWeekDay(museo):
    df = pd.read_sql_table('affluenza', db, parse_dates=True)
    df = df[df['museo_id'] == museo]
    df['weekday'] = df['Data [gg/mm/aaaa]'].dt.dayofweek
    print df
    dfbyday = df.groupby('weekday').sum()
    dfbyday.sum(axis=1)
    return dfbyday.to_json()
    
import pandas as pd
from dom import *
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import create_engine

db = create_engine('mysql://root:root@localhost/torinomusei?charset=utf8')

Session = sessionmaker(bind=db)
session = Session()

def clear_data():
    db.execute('DROP TABLE IF EXISTS collezioni')
    db.execute('DROP TABLE IF EXISTS affluenza')
    db.execute('DROP TABLE IF EXISTS musei')

def populate_musei():
    session.add_all([
                 Museo("GAM"),
                 Museo("MAO"),
                 Museo("Fondo Gabinio")
                 ])
    session.commit()

def populate_collezioni():
    gam = pd.read_csv("http://opendata.fondazionetorinomusei.it/resources/download/COLLEZIONI_GAM.csv", sep=";")
    gam.insert(len(gam.columns), "museo_id", 1)
    gam.to_sql('collezioni', db, if_exists='append', index=False)
    
    mao = pd.read_json("http://opendata.fondazionetorinomusei.it/resources/download/COLLEZIONI_MAO.json")
    mao.insert(len(mao.columns), "museo_id", 2)
    mao = mao.rename(columns={'index':'id'})
    mao.to_sql('collezioni', db, if_exists='append', index=False)
    
#     gab = pd.read_json("./COLLEZIONI_FONDO_GABINIO.json")
#     gab.insert(len(gab.columns), "museo_id", 3)
#     gab.to_sql('collezioni', db, if_exists='append', index=False)

def populate_affluenza():
    gam = pd.read_csv('http://opendata.fondazionetorinomusei.it/resources/download/AFFLUENZA_PUBBLICO_GAM.csv', dayfirst=True, sep=';', parse_dates=['Data [gg/mm/aaaa]'])
    gam.insert(len(gam.columns), "museo_id", 1)
    gam = gam.rename(columns = {'Data [gg/mm/aaaa]' : 'data'})
    gam.to_sql('affluenza', db, if_exists='append', index=False)
    mao = pd.read_csv("http://opendata.fondazionetorinomusei.it/resources/download/AFFLUENZA_PUBBLICO_MAO.csv", dayfirst=True, sep=';' , parse_dates=['Data [gg/mm/aaaa]'])
    mao.insert(len(mao.columns), "museo_id", 2)
    mao = mao.rename(columns = {'Data [gg/mm/aaaa]' : 'data'})
    mao.to_sql('affluenza', db, if_exists='append', index=False)

clear_data()
createDB()
populate_musei()
populate_affluenza()
populate_collezioni()
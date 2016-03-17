import pandas as pd
from dom import *
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import create_engine

db = create_engine('mysql://root:root@localhost/torinomusei?charset=utf8')

Session = sessionmaker(bind=db)
session = Session()

def clear_data():
    db.execute('DROP TABLE IF EXISTS preferiti')
    db.execute('DROP TABLE IF EXISTS collezioni')
    db.execute('DROP TABLE IF EXISTS affluenza')
    db.execute('DROP TABLE IF EXISTS musei')

def populate_musei():
    session.add_all([
                 Museo("GAM"),
                 Museo("MAO"),
                 Museo("Fondo Gabinio"),
                 Museo("Palazzo Madama")
                 ])
    session.commit()

def populate_collezioni():
    gam = pd.read_csv("./COLLEZIONI_GAM.csv", sep=";")
    gam.insert(len(gam.columns), "museo_id", 1)
    gam.to_sql('collezioni', db, if_exists='append', index=False)
    
#     mao = pd.read_csv("./COLLEZIONI_MAO.csv", sep=';')
    mao = pd.read_json("./COLLEZIONI_MAO.json")
    mao.insert(len(mao.columns), "museo_id", 2)
    mao = mao.rename(columns={'index':'id'})
    mao.to_sql('collezioni', db, if_exists='append', index=False)
    
    gab = pd.read_csv("./COLLEZIONI_FONDO_GABINIO.csv", sep=';')
    gab.insert(len(gab.columns), "museo_id", 3)
    gab.to_sql('collezioni', db, if_exists='append', index=False)
    
    madama = pd.read_csv('./COLLEZIONI_PALAZZO_MADAMA.csv', sep=';', encoding='latin-1')
    madama.insert(len(madama.columns), "museo_id", 4)
    madama.to_sql('collezioni', db, if_exists='append', index=False)

def populate_affluenza():
    gam = pd.read_csv('./AFFLUENZA_PUBBLICO_GAM.csv', dayfirst=True, sep=';', parse_dates=['Data [gg/mm/aaaa]'])
    gam.insert(len(gam.columns), "museo_id", 1)
    gam = gam.rename(columns = {'Data [gg/mm/aaaa]' : 'data'})
    gam.to_sql('affluenza', db, if_exists='append', index=False)
    
    mao = pd.read_csv("./AFFLUENZA_PUBBLICO_MAO.csv", dayfirst=True, sep=';' , parse_dates=['Data [gg/mm/aaaa]'])
    mao.insert(len(mao.columns), "museo_id", 2)
    mao = mao.rename(columns = {'Data [gg/mm/aaaa]' : 'data'})
    mao.to_sql('affluenza', db, if_exists='append', index=False)
    
    gab = pd.read_csv("./AFFLUENZA_PUBBLICO_BORGO_MEDIEVALE.csv", dayfirst=True, sep=';' , parse_dates=['Data [gg/mm/aaaa]'])
    gab.insert(len(gab.columns), "museo_id", 3)
    gab = gab.rename(columns = {'Data [gg/mm/aaaa]' : 'data'})
    gab.to_sql('affluenza', db, if_exists='append', index=False)
    
    madama = pd.read_csv("./AFFLUENZA_PUBBLICO_PALAZZO_MADAMA.csv", dayfirst=True, sep=';' , parse_dates=['Data [gg/mm/aaaa]'])
    madama.insert(len(madama.columns), "museo_id", 4)
    madama = madama.rename(columns = {'Data [gg/mm/aaaa]' : 'data'})
    madama.to_sql('affluenza', db, if_exists='append', index=False)

clear_data()
createDB()
populate_musei()
populate_affluenza()
populate_collezioni()
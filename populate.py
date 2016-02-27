import pandas as pd
from sqlalchemy import *
from dom import Collezione, Museo
from sqlalchemy.orm.session import sessionmaker

db = create_engine('mysql://root:root@localhost/torinomusei?charset=utf8')

Session = sessionmaker(bind=db)
session = Session()

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
    mao.to_sql('collezioni', db, if_exists='append', index=False)
    
#     gab = pd.read_json("./COLLEZIONI_FONDO_GABINIO.json")
#     gab.insert(len(gab.columns), "museo_id", 3)
#     gab.to_sql('collezioni', db, if_exists='append', index=False)


# populate_musei()
# populate_collezioni()
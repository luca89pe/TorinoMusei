from flask import Flask
import json
from flask_restful import Resource, Api
import pandas as pd
from dom import Collezione, Museo
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from flask.json import jsonify
import service

db = create_engine('mysql://root:root@localhost/torinomusei?charset=utf8')

Session = sessionmaker(bind=db)
session = Session()

app = Flask(__name__)
api = Api(app)

class Musei(Resource):
    def get(self):    
        return json.dumps(dict(service.FindAllMusei())), 200
        

class Collezioni(Resource):
    def get(self, museo):
        res = service.FindCollezioniMuseo(museo)
        return json.dumps([dict(r) for r in res]), 200
    
class CollezioneSingola(Resource):
    def get(self, collezione):
        return json.dumps([dict(service.FindCollezione(collezione))])

class AffluenzaByWeekDay(Resource):
    def get(self, museo):
        return service.AffluenzaByWeekDay(museo), 200


api.add_resource(Musei, "/musei/")
api.add_resource(Collezioni, "/musei/<int:museo>/")
api.add_resource(AffluenzaByWeekDay, "/musei/<int:museo>/affluenza/")
api.add_resource(CollezioneSingola, "/collezione/<int:collezione>/")


if __name__ == '__main__':
    app.run(debug=True)
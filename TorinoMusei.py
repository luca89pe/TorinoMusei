from flask import Flask
import json
from flask_restful import Resource, Api
import pandas as pd
from dom import Collezione, Museo
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from flask.json import jsonify

db = create_engine('mysql://root:root@localhost/torinomusei?charset=utf8')

Session = sessionmaker(bind=db)
session = Session()

app = Flask(__name__)
api = Api(app)

class Musei(Resource):
    def get(self):
        res = session.query(Museo).all()
        print json.dumps(res)


api.add_resource(Musei, "/musei/")

if __name__ == '__main__':
    app.run(debug=True)
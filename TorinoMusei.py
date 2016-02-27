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
        result = {}
        for row in res:
            result[row.id] = row.name
        return jsonify(result)
    
class Collezioni(Resource):
    def get(self, museo_id):
        res = session.query(Collezione).filter(Collezione.museo_id == museo_id)
        for row in res:
#             print jsonify(row)
#         s = text('SELECT * FROM collezioni WHERE museo_id=:id')
#         s = s.bindparams(id=museo_id)
#         res = (db.execute(s)).fetchall()
            return json.dumps([dict(r) for r in res])


api.add_resource(Musei, "/musei/")
api.add_resource(Collezioni, "/musei/<int:museo_id>/")

if __name__ == '__main__':
    app.run(debug=True)
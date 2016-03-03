from flask import Flask, request, jsonify
import json
from flask_restful import Resource, Api
from dom import Collezione, Museo
import service
from flask.ext.cors import CORS

app = Flask(__name__)
CORS(app)
api = Api(app)

class MuseiLista(Resource):
    def get(self):
        res = service.FindAllMusei()
        return json.dumps([dict(r) for r in res]), 200

class MuseiSingolo(Resource):
    def get(self, museo):
        res = service.FindMuseo(museo)
        return json.dumps(dict(res))

class CollezioniMuseo(Resource):
    def get(self, museo):
        res = service.FindCollezioniMuseo(museo)
        return json.dumps([dict(r) for r in res]), 200
    
class CollezioneSingola(Resource):
    def get(self, museo, collezione):
        res = service.FindCollezione(museo, collezione)
        return json.dumps(dict(res)), 200

class AffluenzaByWeekDay(Resource):
    def get(self, museo):
        res = service.AffluenzaByWeekDay(museo)
        return res, 200

class Signup(Resource):
    def post(self):
        username = request.json.get('username')
        password = request.json.get('password')
        if username is None:
            return 'missing username', 400
        if password is None:
            return 'missing password', 400
        res = service.signup(username, password)
        if res == 'exists':
            return 'the username exists in the database', 400
        else:
            return 'signed up', 201

class Login(Resource):
    def post(self):
        username = request.json.get('username')
        password = request.json.get('password')
        if username is None or password is None:
            return 'missing parameters', 400
        if not service.isUserInDb(username):
            return 'username is not in the DB', 401
        else:
            res = service.generateToken(username, password)
            print res
            if res == 'wrong':
                return 'username and/or password are wrong', 401
            else:
                return json.dumps(dict(res)), 200
            
class Logout(Resource):
    def post(self):
        token = request.json.get('token')
        res=service.deleteToken(token)
        if res == 'token inesistente':
            return 'user is not logged in', 400
        return 'logged out', 200

api.add_resource(MuseiLista, "/musei/")     # Lista di tutti i musei
api.add_resource(MuseiSingolo, "/musei/<int:museo>/")   # Dettagli di un singolo museo, tramite ID
api.add_resource(CollezioniMuseo, "/musei/<int:museo>/collezioni/")     # Lista di tutte le collezioni di un singolo museo
api.add_resource(CollezioneSingola, "/musei/<int:museo>/collezioni/<int:collezione>/")      # Dettagli di una singola collezione
api.add_resource(AffluenzaByWeekDay, "/musei/<int:museo>/affluenza/")       # Affluenza di un singolo museo
api.add_resource(Signup, "/signup")     # Registrazione utente
api.add_resource(Login, "/login")       # Login utente
api.add_resource(Logout,"/logout")      # Logout utente 

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', threaded=True)

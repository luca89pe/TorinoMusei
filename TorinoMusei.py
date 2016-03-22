from flask import Flask, request, jsonify, url_for, send_file
import json
from flask_restful import Resource, Api
from dom import Collezione, Museo
import service
from flask.ext.cors import CORS
from werkzeug import redirect

app = Flask(__name__)
CORS(app)
api = Api(app)

class MuseiLista(Resource):
    def get(self):
        res = service.FindAllMusei()
        print res
        return json.dumps([dict(r) for r in res]), 200

class MuseiSingolo(Resource):
    def get(self, museo):
        res = service.FindMuseo(museo)
        return json.dumps(dict(res))

class CollezioniMuseo(Resource):
    def get(self, museo):
        start = request.args.get('start')
        step = 30
        res = service.FindCollezioniMuseo(museo, start, step)
        print res
        return json.dumps([dict(r) for r in res]), 200
    
class CollezioneSingola(Resource):
    def get(self, museo, collezione):
        res = service.FindCollezione(museo, collezione)
        return json.dumps(dict(res)), 200

class AffluenzaByWeekDay(Resource):
    def get(self, museo):
#         res = service.AffluenzaByWeekDay(museo)
        res = service.MediaAffluenzaByWeekDay(museo)
        print res
        return json.dumps(dict(res)), 200

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
        elif res == 'ko':
            return 'generic error', 400
#             return service.generateToken(username, password), 201
#             return redirect(url_for('login'), code=307)
        print 'return signup2: ',res
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
    def delete(self):
        token = request.json.get('token')
        res=service.deleteToken(token)
        if res == 'token inesistente':
            return 'user is not logged in', 400
        return 'logged out', 200
    
class Ricerca(Resource):
    def get(self):
        query = request.args.get('query')
        searchType = request.args.get('type')
        start = request.args.get('start')
        print query, " - ", searchType, " - ", start
        if query is None or searchType is None or start is None:
            return 'errore argomenti', 404
        res = service.ricerca(query, searchType, start)
        return json.dumps([dict(r.serialize()) for r in res]), 200

class Preferiti(Resource):
    def post(self):
        token = request.json.get('token')
        collezione_id = request.json.get('collezione')
        print token
        print collezione_id
        if token is None or collezione_id is None:
            return 'errore argomenti', 400
        utente_id = service.checkToken(token)
        if utente_id is None:
            return 'token inesistente', 400
        if service.checkCollezione(collezione_id) is None:
            return 'collezione inesistente', 400
        if service.addPreferito(utente_id, collezione_id) is 'exists':
            return 'esiste gia', 200
        return 'added', 201
    
    def get(self):
        token = request.args.get('token')
        print 'getPreferiti: ', token
        if token is None:
            print 'errore argomenti'
            return 'errore argomenti', 400
        utente_id = service.checkToken(token)
        print "risultato di checktoken" , utente_id
        if utente_id is None:
            print 'token inesistente'
            return 'token inesistente', 400
        res = service.findPreferiti(utente_id)
        if not res:
            print 'no preferiti'
            return 'no preferiti', 204
        for r in res:
            print r.serialize()
        return json.dumps([dict(r.serialize()) for r in res])
    
    def delete(self):
        token = request.args.get('token')
        collezione_id = request.args.get('collezione')
        if token is None or collezione_id is None:
            return 'errore argomenti', 400
        utente_id = service.checkToken(token)
        if utente_id is None:
            return 'token inesistente', 400
        if service.checkCollezione(collezione_id) is None:
            return 'collezione inesistente', 400
        service.deletePreferito(utente_id, collezione_id)
        return 'preferito rimosso', 200

class Thumbnail(Resource):
    def get(self):
        url = request.args.get('url')
        print url
        import urllib2 as urllib
        from cStringIO import StringIO
        
        img_file = urllib.urlopen('https://images1-focus-opensocial.googleusercontent.com/gadgets/proxy?url='+url+'&container=focus&resize_h=100')
        im = StringIO(img_file.read())
        print im
        return send_file(im, mimetype='image/jpeg')

class ChangePassword(Resource):
    def put(self):
        token = request.json.get('token')
        password = request.json.get('password')
        newpassword = request.json.get('newpassword')
        if password is None or newpassword is None or token is None:
            return 'errore argomenti', 400
        utente_id = service.checkToken(token)
        if utente_id is None:
            return 'token inesistente', 400
        res = service.changePassword(utente_id, password, newpassword)
        print res
        if res == 'password errata':
            return 'password errata', 400
        return 'changed', 200

class DeleteAccount(Resource):
    def delete(self):
        token = request.json.get('token')
        if token is None:
            return 'errore argomenti', 400
        utente_id = service.checkToken(token)
        if utente_id is None:
            return 'token inesistente', 400
        service.deleteAccount(utente_id)
        return 'utente rimosso', 200
    
class RitornaUtente(Resource):
    def get(self):
        token = request.args.get('token')
        if token is None:
            return 'errore argomenti', 400
        utente_id = service.checkToken(token)
        if utente_id is None:
            return 'token inesistente', 400
        res = service.getUtenteFromId(utente_id)
        return json.dumps(res.serialize()), 200
        

api.add_resource(MuseiLista, "/musei/")     # Lista di tutti i musei
api.add_resource(MuseiSingolo, "/musei/<int:museo>/")   # Dettagli di un singolo museo, tramite ID
api.add_resource(CollezioniMuseo, "/musei/<int:museo>/collezioni")     # Lista di tutte le collezioni di un singolo museo
api.add_resource(CollezioneSingola, "/musei/<int:museo>/collezioni/<int:collezione>/")      # Dettagli di una singola collezione
api.add_resource(AffluenzaByWeekDay, "/musei/<int:museo>/affluenza/")       # Affluenza di un singolo museo
api.add_resource(Preferiti, "/preferiti")    # Aggiungi/Mostra preferiti
api.add_resource(Ricerca, "/search")  # Ricerca
api.add_resource(Signup, "/signup")     # Registrazione utente
api.add_resource(Login, "/login")       # Login utente
api.add_resource(Logout,"/logout")      # Logout utente
api.add_resource(ChangePassword, "/profile/changePassword") # Cambio password utente
api.add_resource(DeleteAccount, "/profile/delete")  # Elimina account
api.add_resource(RitornaUtente, "/profile/utente") # Ritorna l'utente dal token
api.add_resource(Thumbnail, "/thumb")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', threaded=True)

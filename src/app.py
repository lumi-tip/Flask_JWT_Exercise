"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planet, Favorite
#from models import Person

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!
jwt = JWTManager(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/people', methods=['GET','POST'])
def get_all_people():
    if request.method == 'POST':
        name = request.json.get("name")
        hair_color = request.json.get("hair_color")
        if name is None:
            return jsonify({"msg": "name required"})
        if hair_color is None:
            return jsonify({"msg": "hair_color required"})
        new_char = People(name=name, hair_color=hair_color)
        db.session.add(new_char)
        db.session.commit()
        return jsonify({'msg': 'char added successfully'})
    else:
        people = People.query.all()
        return jsonify([char.serialize() for char in people])

@app.route('/people/<int:people_id>')
def get_one_people(people_id):
    character = People.query.filter_by(id = people_id).one_or_none()
    if character is None:
        return jsonify({'msg': 'wrong character id'})
    return jsonify(character.serialize())

@app.route('/planets', methods=['GET','POST'])
def get_all_planets():
    if request.method == 'POST':
        name = request.json.get("name")
        diameter = request.json.get("diameter")
        population = request.json.get("population")
        climate = request.json.get("climate")
        terrain = request.json.get("terrain")
        if name is None:
            return jsonify({"msg": "name required"})
        if diameter is None:
            return jsonify({"msg": "diameter required"})
        if population is None:
            return jsonify({"msg": "population required"})
        if climate is None:
            return jsonify({"msg": "climate required"})
        if terrain is None:
            return jsonify({"msg": "terrain required"})
        
        new_planet = Planet(name=name, diameter=diameter, population=population, climate=climate, terrain=terrain)
        db.session.add(new_planet)
        db.session.commit()
        return jsonify({'msg': 'planet added successfully'})
    else:
        people = People.query.all()
        return jsonify([char.serialize() for char in people])

@app.route('/planet/<int:planet_id>')
def get_one_planet(planet_id):
    planet = Planet.query.filter_by(id = planet_id).one_or_none()
    if planet is None:
        return jsonify({'msg': 'wrong planet id'})
    return jsonify(planet.serialize())

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users])

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get("username")
    password = request.json.get("password")

    user = User.query.filter_by(username = username, password = password).first()

    if user is None:
        return {"msg": "Wrong username or password"}
    
    access_token = create_access_token(identity = user.serialize())
    return jsonify({"token":access_token, "identity": user.serialize()})

@app.route('/users/favorites')
@jwt_required()
def user_favorites():
    user = get_jwt_identity()
    favorites = user.get("favorites")
    if favorites is None:
        return jsonify({'msg': 'no favorites yet'})
    return jsonify(favorites)

@app.route('/favorite/planet/<int:planet_id>', methods=['POST','DELETE'])
@jwt_required()
def add_or_delete_fav_planet(planet_id):
    user = get_jwt_identity()
    if request.method == 'POST':
        new_favorite = Favorite(user_id = user['id'], planet_id = planet_id)
        if new_favorite.planet_id is None:
            return jsonify({'msg': 'wrong planet id'})
        db.session.add(new_favorite)
        db.session.commit()
        return jsonify({'msg': 'Favorite added'})
    else:
        del_favorite = Favorite.query.filter_by(user_id = user['id'], planet_id = planet_id).one_or_none()
        if del_favorite is None:
            return jsonify({'msg': 'wrong planet id'})
        db.session.delete(del_favorite)
        db.session.commit()
        return jsonify({'msg': 'favorite planet deleted'})

@app.route('/favorite/people/<int:people_id>', methods=['POST','DELETE'])
@jwt_required()
def add_or_delete_fav_char(people_id):
    user = get_jwt_identity()
    if request.method == 'POST':
        new_favorite = Favorite(user_id = user['id'], people_id = people_id)
        if new_favorite.people_id is None:
            return jsonify({'msg': 'wrong char id'})
        db.session.add(new_favorite)
        db.session.commit()
        return jsonify({'msg': 'Favorite added'})
    else:
        del_favorite = Favorite.query.filter_by(user_id = user['id'], people_id = people_id).one_or_none()
        if del_favorite is None:
            return jsonify({'msg': 'wrong character id'})
        db.session.delete(del_favorite)
        db.session.commit()
        return jsonify({'msg': 'favorite character deleted'})

    

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique = True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "favorites": [favorite.serialize() for favorite in self.favorites] if self.favorites else None
            # do not serialize the password, its a security breach
        }

class Planet(db.Model):
    __tablename__ = "planets"

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String, nullable = False)
    diameter = db.Column(db.Integer, nullable = False)
    population = db.Column(db.Integer, nullable = False)
    climate = db.Column(db.String, nullable = False)
    terrain = db.Column(db.String, nullable = False)

    def __repr__(self):
        return '<Planet %r>' % self.name
    
    def __init__(self,name, diameter, population, climate, terrain):
        self.name = name
        self.diameter = diameter
        self.population = population
        self.climate = climate
        self.terrain = terrain

    def serialize(self):
        return{
            "id": self.id,
            "name": self.name,
            "diameter": self.diameter,
            "population": self.population,
            "climate": self.climate,
            "terrain": self.terrain,
        }

class People(db.Model):
    __tablename__ = "people"
    
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String, nullable = False)
    hair_color = db.Column(db.String, nullable = True)
    homeplanet_id = db.Column(db.Integer, db.ForeignKey(Planet.id))
    homeplanet = db.relationship(Planet, backref = "stellar_citizens")

    def __repr__(self):
        return '<People %r>' % self.name
    
    def __init__(self, name, hair_color):
        self.name = name
        self.hair_color = hair_color

    def serialize(self):
        return{
            "id": self.id,
            "name": self.name,
            "hair_color": self.hair_color
        }

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key = True)

    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship(User, backref = "favorites")
    
    planet_id = db.Column(db.Integer, db.ForeignKey(Planet.id), nullable = True)
    planet = db.relationship(Planet, backref = "favorites")
    
    people_id = db.Column(db.Integer, db.ForeignKey(People.id), nullable = True)
    people = db.relationship(People, backref = "favorites")

    def __repr__(self):
        return '<Favorite %r>' % self.id

    def serialize(self):
        return{
            "id": self.id,
            "name": self.user.username,
            "planet": self.planet.name if self.planet else None,
            "people": self.people.name if self.people else None,
        }

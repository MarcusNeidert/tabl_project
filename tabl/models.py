"""
This file contains the declarations of the models.
"""

from dataclasses import dataclass
from tabl import db, login_manager
from flask_login import UserMixin, LoginManager



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


#ASSOCIATION TABLES
intolerances = db.Table('intolerances',
                        db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                        db.Column('ingredient_id', db.Integer, db.ForeignKey('ingredient.id'), primary_key=True)
                        )

user_cookware = db.Table('user_cookware',
                         db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                         db.Column('cookware_id', db.Integer, db.ForeignKey('cookware.id'), primary_key=True)
                         )
@dataclass  # dataclass is used to allow for converting objects to JSON in the webservice
class User(db.Model, UserMixin):
    is_admin   = db.Column(db.Boolean, nullable=False, default=False)
    id         = db.Column(db.Integer, primary_key=True)
    username   = db.Column(db.String(20), unique=True, nullable=False)
    email      = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='tabl.png')
    password   = db.Column(db.String(60), nullable=False)

    #users will be able to search from a list of ingredients, cookware and styles to add to their profile
    user_intolerances = db.relationship('Ingredient', secondary=intolerances, lazy='subquery',
                                        backref=db.backref('intolerant', lazy=True))
    cookware          = db.relationship('Cookware', secondary=user_cookware, lazy='subquery',
                               backref=db.backref('cookware', lazy=True))
    user_style_id     = db.Column(db.Integer, db.ForeignKey('style.id'), nullable=False, default=0)

    def __repr__(self):
        return f"<User(id='{self.id}', username='{self.username}', email='{self.email}', image_file='{self.image_file}', cooking_style = '{self.style}', cookware = '{self.cookware}', intolerances = '{self.user_intolerances}')>"


class Ingredient(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    name     = db.Column(db.String(40), unique=True, nullable=False)
    category = db.Column(db.String(20), nullable=False) #Every ingredient belongs to a category (protein, spice, carbohydrates etc)

    def __repr__(self):
        return f"<Ingredient(name='{self.name}', category='{self.category}')>"

class Cookware(db.Model):
    id   = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), unique=True, nullable=False)

    def __repr__(self):
        return f"<Cookware(name='{self.name}')>"

class Style(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(40), unique=True, nullable=False)
    style_users = db.relationship(User, backref='style', lazy=True) #many-to-one relationship. Each style can have many users, but the users can choose only one favourite style.

    def __repr__(self):
        return f"<Style(name='{self.name}')>"


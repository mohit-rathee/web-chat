from .. import db, Base
from flask import Blueprint

models = Blueprint('models',__name__)

class users(Base):
    __tablename__="users"
    id=db.Column(db.Integer,primary_key=True)                   #User ID
    username=db.Column(db.String, unique=True, nullable=False)  #user name
    password=db.Column(db.String, nullable=False)               #user password
    description=db.Column(db.String, nullable=True)             #user bio

class channel(Base):
    __tablename__="channel"
    id=db.Column(db.Integer,primary_key=True)                   #topic ID
    name=db.Column(db.String, nullable=False)                   #topic name
    creator_id=db.Column(db.Integer,db.ForeignKey('users.id'))  #creator ID
    description=db.Column(db.String, nullable=True)             #description
    user=db.relationship('users')
     
class media(Base):
    __tablename__="media"
    id=db.Column(db.Integer,primary_key=True)
    hash=db.Column(db.String,unique=True)
    name=db.Column(db.String, nullable=False)

class admin(Base):
    __tablename__="admin"
    id=db.Column(db.Integer,primary_key=True) #Conventional key
    #key=db.Column(db.String,unique=True)
    value=db.Column(db.String) #Respective value


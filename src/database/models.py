from enum import unique
from .. import db, Base
from flask import Blueprint

models = Blueprint('models',__name__)

class users(Base):
    __tablename__="users"
    id=db.Column(db.Integer,primary_key=True)                   #User ID
    username=db.Column(db.String, unique=True, nullable=False)  #user name
    password=db.Column(db.String, nullable=False)               #user password
    description=db.Column(db.String, nullable=True)             #user bio
    role_id=db.Column(db.Integer,db.ForeignKey('roles.id'))     #Role ID
    role=db.relationship('roles',back_populates="user")

class roles(Base):
    __tablename__="roles"
    id=db.Column(db.Integer, primary_key=True)                  #Role ID
    design=db.Column(db.String, unique=True, nullable=False)    #Designation Name
    referals=db.Column(db.String, nullable=True)                #Registration Code
    # Permissions
    is_channel=db.Column(db.Integer)
    is_media=db.Column(db.Integer)
    is_admin=db.Column(db.Integer)
    user=db.relationship('users',back_populates="role")
    

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
    permissions=db.Column(db.String, nullable=False)

class status(Base):
    __tablename__="status"
    key=db.Column(db.Integer,primary_key=True)                  #Conventional key
    value=db.Column(db.String)                                  #Respective value
# EXAMPLE
#   name : UIET
#   description  :  this is for uietians.
#   uuid  :  2j3e23w23823u029eh23
#   defualt role :  3 (for new users)
#   registration  :  1/0 (True/False)

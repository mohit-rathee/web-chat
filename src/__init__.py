from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from flask_socketio import SocketIO
from gevent import monkey
from flask_session import Session
from config import Config

monkey.patch_all()


app = Flask(__name__)

# Configurations go here
app.config.from_object(Config)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Connecting to Main Database.
engine=create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
metadata=MetaData()
metadata.bind=engine
Base=declarative_base(metadata=metadata)

# Session management.
app.config["SESSION_PERMANENT"]=False
app.config["SESSION_TYPE"]="filesystem"

session = Session(app)


# Setting up app with Flask.
socketio = SocketIO(app, async_mode='gevent', transport=['websocket'], manage_session=False)

engine={"app":engine}
base={"app":Base}
server={}
tables = {}

socketio.server.manager.rooms['/']={}
rooms=socketio.server.manager.rooms['/']


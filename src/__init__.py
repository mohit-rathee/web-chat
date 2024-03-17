from flask import Flask
import os, pytz
from bidict import bidict
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from flask_socketio import SocketIO
from gevent import monkey
from flask_session import Session
from config import Config

monkey.patch_all()

# Creating some Important folder.
db_dir = os.path.join('db')
media_dir = os.path.join('media_files')
if not os.path.exists(media_dir):
    os.makedirs(media_dir)
if not os.path.exists(db_dir):
    os.makedirs(db_dir)

app = Flask(__name__,static_folder='../static')

# Configurations go here
app.config.from_object(Config)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Connecting to Main Database.
Engine=create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
metadata=MetaData()
metadata.bind=Engine
Base=declarative_base(metadata=metadata)

# Session management.
app.config["SESSION_PERMANENT"]=False
app.config["SESSION_TYPE"]="filesystem"

session = Session(app)


# Setting up app with Flask.
socketio = SocketIO(
    app,
    async_mode='gevent',
    transport=['websocket'],
    manage_session=False)

engine={"app":Engine}
base={"app":Base}
server={}
tables = {"app" : {"Name" : "app"}}
# Manually creating spaces and rooms in socketio. coz I m A-Fish-ant.
rooms={'app':bidict({})} # Structure is lib specific.

india_timezone = pytz.timezone('Asia/Kolkata')

from .database.database_utils import load_channels
load_channels("app",base["app"],engine["app"])

from .database.database_utils import get_server_status, create_server_status
if not get_server_status("app"):
    create_server_status("app","app","")

socketio.server.manager.rooms['/']=rooms
#rooms=socketio.server.manager.rooms['/']

from .routes.routes import routes
from .database.models import models, roles
from .sockets.sockets_routes import sockets
from .media.media import medias

app.register_blueprint(routes)
app.register_blueprint(models)
app.register_blueprint(sockets)
app.register_blueprint(medias)

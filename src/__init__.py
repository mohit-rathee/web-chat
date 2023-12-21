from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base



app = Flask(__name__)

# Configurations go here
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Connecting to Main Database.
engine=create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
metadata=MetaData()
metadata.bind=engine
Base=declarative_base(metadata=metadata)

engine={"app":engine}
base={"app":Base}
server={}


# Import other modules for them to run their setup
from .models import models
from .controllers import main_controller, admin_controller
from .sockets import socket_handler


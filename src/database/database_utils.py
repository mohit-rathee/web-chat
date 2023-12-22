from .. import db, engine, server, tables, rooms, base
from bidict import bidict
from sqlalchemy import create_engine, MetaData, Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

def create_channel(table_number,base,users):
    attrs = {
        '__tablename__': str(table_number),
        'id': db.Column(db.Integer, primary_key=True),
        'data': db.Column(db.String, nullable=False),
        'sender_id': db.Column(db.Integer, db.ForeignKey(users.id)),
        'user': db.relationship(users)
    }
    channel_class = type(str(table_number), (base,), attrs)
    return channel_class

def create_conn(name,uri):
    Engine = create_engine(uri)
    Engine.connect()
    engine[name]=Engine
    metadata=MetaData()
    metadata.bind=Engine
    Base=declarative_base(metadata=metadata)
    # coping these 3 table structure from Main Database.
    req=["users","channel","media","admin"]
    for table_name in req:
        table = base["app"].metadata.tables.get(table_name)
        table.tometadata(metadata)
    # reviving the user realtionships. this is too daam awkward.
    class users(Base):
        __tablename__ = "users"
        __table_args__ = {"extend_existing": True}
        id = Column(db.Integer, primary_key=True)
        username = Column(db.String, unique=True, nullable=False)
        password = Column(db.String, nullable=False)
        description=db.Column(db.String, nullable=True)
    # Creating tables and storing session.
    Base.metadata.create_all(bind=Engine)
    #app.config['SQLALCHEMY_BINDS'][name]=db_uri
    base[name]=Base
    Session=sessionmaker(bind=Engine)
    server[name]=Session()
    # setup
    #setup(server[name])
    # Initialising room for the database.
    tables[name]={'Len':0}
    rooms[name]=bidict({})

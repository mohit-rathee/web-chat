from .. import db, engine, server, tables, rooms, base
from ..database.models import channel, users, roles, status
import uuid , bcrypt
from bidict import bidict
from sqlalchemy import create_engine, MetaData, Column, false, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Loading data from Main Database.
def load_channels(db,base,engine):
    inspector = inspect(engine)
    tbls = inspector.get_table_names()
    tables[db]["Len"]=len(tbls)
    for tb in tbls:
        if tb.isdigit():
            tables[db][int(tb)]=new_channel_class(tb, base,users)
    # Recreating the session.
    base.metadata.create_all(bind=engine)
    sqlsession=sessionmaker(bind=engine)
    server[db]=sqlsession()

def new_channel_class(table_number,base,users):
    attrs = {
        '__tablename__': str(table_number),
        'id': Column(db.Integer, primary_key=True),
        'data': Column(db.String, nullable=False),
        'sender_id': Column(db.Integer, db.ForeignKey(users.id)),
        'user': db.relationship(users)
    }
    channel_class = type(str(table_number), (base,), attrs)
    return channel_class


def create_channel(curr,newchannel,creator_id):
    Topic=channel(name=newchannel,creator_id=creator_id,description=None)
    server[curr].add(Topic)
    server[curr].commit()
    Base=base[curr]
    tables[curr][Topic.id]=new_channel_class(Topic.id,Base,users)
    tables[curr]["Len"]+=1
    Base.metadata.create_all(engine[curr])
    new={"channel":[curr,Topic.id,Topic.name,Topic.user.username]}
    return new

def create_connection(db_name,uri):
    try:
        Engine = create_engine(uri)
        Engine.connect()
        engine[db_name]=Engine
        metadata=MetaData()
        metadata.bind=Engine
        Base=declarative_base(metadata=metadata)
        # coping these 3 table structure from Main Database.
        req=["users","channel","media","status","roles"]
        for table_name in req:
            table = base["app"].metadata.tables.get(table_name)
            table.tometadata(metadata)
        # reviving the user realtionships. this is awkward.
        class users(Base):
            __tablename__ = "users"
            __table_args__ = {"extend_existing": True}
            id = Column(db.Integer, primary_key=True)
            username = Column(db.String, unique=True, nullable=False)
            password = Column(db.String, nullable=False)
            description= Column(db.String, nullable=True)
            role_id= Column(db.Integer,db.ForeignKey(roles.id))
            role= db.relationship(roles,foreign_keys=[role_id])
            
        # Creating tables and storing session.
        #app.config['SQLALCHEMY_BINDS'][name]=db_uri
        Base.metadata.create_all(bind=Engine)
        sqlsession=sessionmaker(bind=Engine)
        server[db_name]=sqlsession()
        base[db_name]=Base
        # setting up Admin role
        #setup(server[name])
        # Initialising room for the database.
        status = get_server_status(db_name)
        if status:
            # get details and update memory
            db_uuid = status["uuid"]
            server[db_uuid]=server.pop(db_name)
            engine[db_uuid]=engine.pop(db_name)
            base[db_uuid]=base.pop(db_name)
            tables[db_uuid]={'Len':0,"Name":status["name"]}
            load_channels(db_uuid,Base,Engine)
            rooms[db_uuid]=bidict({})
            return [True]
        else:
            return [False]
    except:
        server.pop(db_name,None)
        return False

def admin_role(db):
    Admin=roles(design="Admin",is_channel=1, is_media=1, is_admin=1)
    server[db].add(Admin)
    server[db].commit()
    return Admin

def guest_role(db):
    Guest=roles(design="Guest",is_channel=0, is_media=0, is_admin=0)
    server[db].add(Guest)
    server[db].commit()
    return Guest.id

def check_credential(db,name,pswd):
    user = server[db].query(users).filter_by(username=name).first()
    if user!=None:
        if bcrypt.checkpw(pswd, user.password):
            return [user.username,user.id]
        else:
            return [False]

def get_default_role(db):
    role = server[db].query(status).filter_by(key=3).first()
    return int(role.value)

def create_server_status(db,name,desc):
    guest_role_id = guest_role(db)
    unique_id = str(uuid.uuid4())
    srvr_name = status(key=1,value=name)
    srvr_uuid = status(key=2,value=unique_id)
    srvr_default = status(key=3,value=guest_role_id)
    srvr_desc = status(key=4,value=desc)
    server[db].add(srvr_name)
    server[db].add(srvr_uuid)
    server[db].add(srvr_default)
    server[db].add(srvr_desc)
    server[db].commit()
    return {
        "name":name,
        "uuid":unique_id,
        "default":guest_role_id,
        "desc":desc
    }

def get_server_status(db):
    any_admin= server[db].query(roles).filter_by(is_admin=1).first()
    if not any_admin :
        admin_role(db)
        # maybe randomly put anybody into admin role.
    db_status = server[db].query(status).all() 
    if db_status:
        return {
            "name":db_status[0].value,
            "uuid":db_status[1].value,
            "default":db_status[2].value,
            "desc":db_status[3].value
        }
    else:
        return False

def add_user(db,name,pswdHash,role):
    user=users(username=name,password=pswdHash,role_id=role)
    server[db].add(user)
    server[db].commit()
    return [user.id,user.username]

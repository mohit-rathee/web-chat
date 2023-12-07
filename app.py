import os, uuid, asyncio, mimetypes, hashlib , datetime, pytz, json, time
from bidict import bidict
from datetime import timedelta
from flask import Flask, render_template, request, redirect, session, make_response, Response
from werkzeug.utils import secure_filename
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
from flask import send_file
from passlib.hash import sha256_crypt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy import create_engine, MetaData, Column, text, String, ForeignKeyConstraint
from sqlalchemy.ext.declarative import declared_attr, declarative_base
from flask_socketio import SocketIO, join_room, emit, leave_room,send
import gevent
from gevent import monkey
monkey.patch_all()
app = Flask(__name__)
app.debug=True
app.config.from_object(__name__)
socketio = SocketIO(app, async_mode='gevent', transport=['websocket'], manage_session=False)
app.config['SECRET_KEY'] =os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SQLALCHEMY_DATABASE_URI'] =os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_BINDS']={}
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=60)
india_timezone = pytz.timezone('Asia/Kolkata')
db = SQLAlchemy(app)
engine=create_engine(os.getenv('DATABASE_URI'))
metadata=MetaData(bind=engine)
Base=declarative_base(metadata=metadata)
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
# class chats(Base):          # I decided to make chats only store at client side.
#     __tablename__="chats"   # Sever will be used to just transfer encrypted message.
#     id=db.Column(db.Integer,primary_key=True)     #This way I can
#     key=db.Column(db.String,nullable=False)       #implement p2p encryption.
#     data=db.Column(db.String, nullable=False)     #in JavaScript
class media(Base):
    __tablename__="media"
    id=db.Column(db.Integer,primary_key=True)
    hash=db.Column(db.String,unique=True)
    name=db.Column(db.String, nullable=False)
def create_channel(table_number,base,users):
    attrs = {
        '__tablename__': str(table_number),
        'id': Column(db.Integer, primary_key=True),
        'data': Column(db.String, nullable=False),
        'sender_id': Column(db.Integer, db.ForeignKey(users.id)),
        'user': db.relationship(users)
    }
    channel_class = type(str(table_number), (base,), attrs)
    return channel_class
inspector = inspect(engine)
tbls = inspector.get_table_names()
Tables={"app":{'Len':len(tbls)}}
for tb in tbls:
    if tb.isdigit():
        Tables["app"][int(tb)]=create_channel(tb, Base,users)
Base.metadata.create_all(bind=engine)
sqlsession=sessionmaker(bind=engine)
app.config["SESSION_PERMANENT"]=False
app.config["SESSION_TYPE"]="filesystem"
Session(app)
engine={"app":engine}
server={"app":sqlsession()}
base={"app":Base}
socketio.server.manager.rooms['/']={}
rooms=socketio.server.manager.rooms['/']
rooms['app']=bidict({})
mediaHash={}
uploads_dir = os.path.join('db')
if not os.path.exists(os.path.join("media")):
    os.makedirs(os.path.join("media"))
if not os.path.exists(os.path.join("db")):
    os.makedirs(os.path.join("db"))
@app.route('/create',methods=["POST"])
def createdb():
    name=str(request.form.get("name"))
    if " " in name:
        return render_template("message.html",msg="Don't use spaces", goto="/login")
    if name in server or "/" in name:
        return render_template("message.html",msg="select a unique and valid name.",goto="/")
    db_uri = f'sqlite:///db/{name}.sqlite3'
    Engine = create_engine(db_uri)
    Engine.connect()
    engine[name]=Engine
    metadata=MetaData(bind=Engine)
    Base=declarative_base(metadata=metadata)
    req=["serverinfo","users","channel","chats","media"]
    Tables[name]={'Len':0}
    rooms[name]=bidict({})
    for table_name in req:
        table = base["app"].metadata.tables.get(table_name)
        table.tometadata(metadata)
    class users(Base):
        __tablename__ = "users"
        __table_args__ = {"extend_existing": True}
        id = Column(db.Integer, primary_key=True)
        username = Column(db.String, unique=True, nullable=False)
        password = Column(db.String, nullable=False)
        description=db.Column(db.String, nullable=True)
    Base.metadata.create_all(bind=Engine)
    app.config['SQLALCHEMY_BINDS'][name]=db_uri
    base[name]=Base
    Session=sessionmaker(bind=Engine)
    server[name]=Session()
    return redirect("/login")
@app.route('/upload',methods=["POST"])
def upload_db():
    files=request.files.getlist('files')
    for file in files:
        filename=(secure_filename(file.filename).split("."))
        if not file or filename[1]!="sqlite3" or filename[0] in server:
            return render_template("message.html",msg="select a valid database file (*.sqlite3) with unique name.",goto="/login")
        uploads_dir = os.path.join('db')
        file.save(os.path.join(uploads_dir,secure_filename(file.filename)))
        name=filename[0]
        app.config['SQLALCHEMY_BINDS'][name] ="sqlite:///"+str(os.path.join(uploads_dir,secure_filename(file.filename)))
        try:
            Engine = create_engine(app.config['SQLALCHEMY_BINDS'][str(name)])
            metadata = MetaData(bind=engine)
            Base = declarative_base(metadata=metadata)
            class users(Base):
                __tablename__ = "users"
                __table_args__ = {"extend_existing": True}
                id = Column(db.Integer, primary_key=True)
                username = Column(db.String(20), unique=True, nullable=False)
                password = Column(db.String(30), nullable=False)
            Base.metadata.create_all(bind=Engine)
            inspector = inspect(Engine)
            tbls = inspector.get_table_names()
            Tables[name]={'Len':len(tbls)}
            for tb in tbls:
                if tb.isdigit():
                    Tables[name][int(tb)]=create_channel(tb, Base,users)
            Base.metadata.create_all(bind=Engine)
            base[name]=Base
            engine[name]=Engine
            Session=sessionmaker(bind=Engine)
            server[name]=Session()
            rooms[name]=bidict({})
        except:
            app.config['SQLALCHEMY_BINDS'].pop(name,None)
            os.remove("db/"+name+".sqlite3")
            server.pop(name,None)
            session.clear()
            return render_template("message.html",msg="NOT A VALID DATABASE",goto="/login")
        session.clear()
    return redirect("/login")
#  WHEN HAVE TO DELETE THE SERVER(not up-to-date)
    #     os.remove("db/"+str(deldb).rsplit("-")[1])
    #     app.config['SQLALCHEMY_DATABASE_URI'] ="sqlite:///db.sqlite3"
    #     return redirect("/servers")
@socketio.on('setPubKey')
def handel_Pub_Key(pub_key):
    if isinstance(pub_key,str) and len(pub_key):
        mydata=rooms[request.sid]
        mydata.inverse[mydata[request.sid]]=pub_key
@socketio.on('disconnect')
def on_disconnect():
    # could just pop those values 
    socketio.server.leave_room(request.sid, room=None)
    socketio.server.leave_room(request.sid, room=request.sid)
    for srvr in session.get("myserver"):
        rooms[srvr].pop(session.get(srvr),None)
        # I m doing this because I don't want to delete the bidict({}) if empty
        # socketio.server.leave_room(session.get(srvr),room=srvr)
        socketio.emit("notify",[srvr,session.get(srvr),session.get("name"),None],room=srvr) 
@socketio.on('Load')
def Load(data):
    reqsrvr=data.get('server')
    if reqsrvr in session.get('myserver'): # And wheater the reqsrvr is in server.keys()
        id=session.get(reqsrvr)
        (pub_key,eio_sid)=next(iter(rooms[request.sid].items()))
        socketio.emit("notify",[reqsrvr,id,session.get("name"),pub_key],room=reqsrvr)
        rooms[reqsrvr][id]=eio_sid
        serverInfo={'server':reqsrvr,'id':id}
        curr=server[reqsrvr]
        channels=curr.query(channel).all() #later on we can limit this for sync sliding
        chnlCount=len(data.get("msg",0))   # I can definately use the dict which store
        serverInfo['channels']={}          # all the channels i just need time.
        for chnl in channels:
            if chnl.id>chnlCount:
                serverInfo['channels'][chnl.id]=[chnl.id,chnl.name,chnl.user.username]
        Media=curr.query(media).filter(media.id>data.get('media',0)).all()
        serverInfo['medias']={media.id:[media.id,media.hash,media.name] for media in Media}
        User=curr.query(users).all()
        serverInfo['users']={user.id:user.username for user in User}
        Dict={}
        for id,eid in rooms[reqsrvr].items():
            sid=rooms[None].inverse.get(eid)
            (pub_key,_)=next(iter(rooms[sid].items()))
            Dict.update({id:pub_key})
        serverInfo['live']=Dict
        socketio.emit("server",serverInfo,to=request.sid)
        for chnl in channels:
            lastid=data.get('msg').get(str(chnl.id),0)
            ch=Tables[reqsrvr][chnl.id]
            last_msgs=curr.query(ch).order_by(ch.id.desc()).filter(ch.id>lastid).limit(30)
            Msgs=[reqsrvr,chnl.id]
            Msgs.append([[msg.id,msg.data,msg.user.username] for msg in last_msgs])
            socketio.emit("messages",Msgs,to=request.sid)
@socketio.on("create")
def create(newchannel):
    curr=newchannel[0]
    if curr not in session.get("myserver"):
        return
    id=session.get(curr)
    Topic=channel(name=newchannel[1],creator_id=id)
    server[curr].add(Topic)
    server[curr].commit()
    Base=base[curr]
    Tables[curr][Topic.id]=create_channel(Topic.id, Base,users)
    Tables[curr]["Len"]+=1
    Base.metadata.create_all(engine[curr])
    new={"channel":[curr,Topic.id,Topic.name,Topic.user.username]}
    socketio.emit("show_this",new,room=curr)
# @socketio.on("search_text")
# def search(text):
#    curr=session.get("server")
#    user_list=server[curr].query(users).filter(users.username.like("%"+text+"%")).all()
#    Users={"users":[user.username for user in user_list]}
#    socketio.emit("show_this",Users,to=request.sid)
@socketio.on('message')
def handel_message(message):
    msg={}
    msgData=message.get('msgData')
    if msgData:
        msg[0]=msgData
    curr=message.get('server')
    if curr not in session.get("myserver"):
        return
    mediaId=message.get('mediaId')
    if mediaId:
        Media=server[curr].query(media).filter_by(id=mediaId).first()
        if Media==None:
            return
        msg[1]=mediaId
    id=session.get(curr)
    name=session.get("name")
    channel_id=int(message.get('channel'))
    msg[3]=datetime.datetime.now(india_timezone).strftime('%d-%m-%Y %H:%M:%S')
    if channel_id <= Tables[curr]['Len']:
        replyId=message.get('replyId')
        if replyId:
            reply=server[curr].query(Tables[curr][channel_id]).filter_by(id=int(replyId)).first()
            if reply==None:
                return
            msg[2]=replyId
        Msg=json.dumps(msg)
        message=Tables[curr][channel_id](data=Msg,sender_id=id)
        server[curr].add(message)
        server[curr].commit()
        socketio.emit('show_message',[curr,channel_id,message.id,msg,name], room = curr)
@socketio.on('chat')
def handel_chat(chat):
    curr=chat.get('server')
    reciever=chat.get('id')
    msg=chat.get('msg')
    if curr not in session.get('myserver') or not msg or not isinstance(reciever,int):
        return
    id=session.get(curr)
    resvrEID=socketio.server.manager.rooms['/'][curr].get(reciever)
    if resvrEID:
        resvrSID=socketio.server.manager.rooms['/'][None].inverse.get(resvrEID)
        socketio.emit('dm',[curr,id,msg],to=resvrSID)
    else:
        print('friend is offline')

@socketio.on('reaction')
def reaction(Data):
    curr=Data[0]
    if curr not in session.get("myserver"):
        return
    id=session.get(curr)
    channel_id=int(Data[1])
    # FOR CHANNEL
    if channel_id <= Tables[curr]['Len']:
        msg=server[curr].query(Tables[curr][channel_id]).filter_by(id=Data[2]).first()
        if msg:
            message=json.loads(msg.data)
            if Data[3]:
                if message.get('4'):
                    message['4'][str(id)]=Data[3]
                else:
                    message['4']={str(id):Data[3]}
            else:
                message['4'].pop(str(id))
                Data[3]=None
            data=json.dumps(message)
            msg.data=data
            server[curr].commit()
            socketio.emit('reaction',[curr,channel_id,msg.id,id,Data[3]],to=curr)
@socketio.on('getHistory')
def getHistory(data):
    curr=data.get("server")
    try:
        lastMsg=int(data.get('lastMsg'))
        channelId=int(data.get('channel'))
    except:
        return
    if curr in session.get("myserver") and channelId <= Tables[curr]['Len']:
        channel=Tables[curr][channelId]
        last_msgs=server[curr].query(channel).order_by(channel.id.desc()).filter(channel.id<lastMsg).limit(30)
        Msgs=[[msg.user.username,msg.id,msg.data] for msg in last_msgs]
        Msgs=[curr,channelId]
        Msgs.append([[msg.id,msg.data,msg.user.username] for msg in last_msgs])
        socketio.emit("messages",Msgs,to=request.sid)
@app.route('/',methods=["GET","POST"])
def index():
    if request.method=="GET":
        if session.get("name")==None:
            return redirect("/login")
        else:
            return redirect("/channels")
    session.clear()
    return redirect("/")
def loginlogic(name,password):
    myServer=session.get("myserver")
    pswdHash=None
    if myServer!=None:
        session["server"]=myServer[0]
        user=server[myServer[0]].query(users).filter_by(id=session.get(myServer[0])).first()
        pswdHash=user.password
    else:
        myServer=[]
    undone=[]
    for srvr in server.keys():
        if srvr not in myServer:
            user = server[srvr].query(users).filter_by(username=name).first()
            if user!=None:
                if pswdHash==None:
                    if sha256_crypt.verify(str(name+password), user.password):
                        pswdHash=user.password
                        session["server"]=srvr
                        session["name"]=name
                        session[srvr]=user.id
                        myServer.append(srvr)
                    else:
                        undone.append(srvr)
                else:
                    if pswdHash != user.password:
                        if sha256_crypt.verify(str(name+password), user.password):
                            user.password=pswdHash
                            server[srvr].commit()
                        else:
                            user.password=pswdHash
                            server[srvr].commit()
                    myServer.append(srvr)
                    session[srvr]=user.id
    if len(myServer)==0:
            return False
    for srvr in undone:
        user = server[srvr].query(users).filter_by(username=name).first()
        user.password=pswdHash
        server[srvr].commit()
        myServer.append(srvr)
        session[srvr]=user.id
    session["myserver"]=myServer[:]
    return True
@app.route('/login',methods=["GET","POST"])
def login():
    # REDIRECT IF LOGGED IN
    if request.method=="GET":
        if session.get("name")==None:
            allServers=[]
            for srvr in server.keys():
                allServers.append(srvr)
            return render_template("login.html",servers=allServers)
        else:
            return redirect("/channels")
    else:
        session.clear()
        name=str(request.form.get("username"))
        password=str(request.form.get("password"))
        operation=request.form.get("operation")
        if operation == "login":
            done=loginlogic(name, password)
            if done:
                return redirect("/channels")
            else:
                return render_template("message.html",msg="Username or password are incorrect",goto="/login")
        if operation == "register":
            pswdHash=""
            myserver=[]
            serverList=request.form.getlist("server[]")
            if len(serverList)==0:
                return render_template("message.html",msg="Select atleast one server", goto="/login")
            for srvr in serverList:
                user=server[srvr].query(users).filter_by(username=name).first()
                if user!=None:
                    if sha256_crypt.verify(str(name+password), user.password):
                        pswdHash=user.password
                        session[srvr]=user.id
                        myserver.append(srvr)
                        session["name"]=user.username
                    else:
                        return render_template("message.html",msg="Username exist",goto="/login")
            if not pswdHash:
                pswdHash=sha256_crypt.encrypt(str(name+password))
            for srvr in serverList:
                if srvr not in myserver:
                    user=users(username=name,password=pswdHash)
                    server[srvr].add(user)
                    server[srvr].commit()
                    session[srvr]=user.id
                    session["name"]=user.username
                    myserver.append(srvr)
            session["myserver"]=myserver[:]
            session["server"]=myserver[0]
            if len(serverList)==len(server):
                return redirect("/channels")
            done=loginlogic(name, password)
            if done:
                return redirect("/channels")
            else:
                return render_template("message.html",msg="YOUR OLD PASSWORD IS UPDATED WITH NEWONE",goto="/channels")
@app.route("/media/<srvr>/<id>",methods=["GET"])
def handel_get_Media(srvr,id):
    if srvr not in session.get("myserver"):
        return "0"
    Media=server[srvr].query(media).filter_by(id=id).first()
    if Media != None:
        file_path="media/"+Media.hash
        if os.path.exists(file_path):
            return send_file(file_path)
        else:
            return make_response('Not found',404)
    else:
        return make_response('Not found',404)
@app.route("/media",methods=["POST"])
def handel_media():
    def uploadSuccess(unique_id,file_hash):
        curr=mediaHash[unique_id][3]
        session=server[curr]
        check=session.query(media).filter_by(hash=file_hash).first()
        if check==None:
            data=mediaHash[unique_id]
            name=[data[1],data[2]] #store only name & typ 
            Media=media(hash=file_hash,name=json.dumps(name))
            session.add(Media)
            session.commit()
            os.rename("media/"+unique_id,"media/"+file_hash) #file uploaded
            socketio.emit("media",[curr,Media.id,Media.hash,name],room=curr)
            return Media.id
        elif not os.path.exists("media/"+file_hash): #file is reuploaded and saved
            os.rename("media/"+unique_id,"media/"+file_hash)
            return check.id
        else:
            os.remove("media/"+unique_id) # duplicate file deleted
            return 0
    unique_id=request.form.get('uuid')
    if unique_id:
        chunk=request.files['chunk'].read()
        hasher = mediaHash[unique_id][0]
        hasher.update(chunk)
        with open("media/"+unique_id,"ab") as file:
            file.write(chunk)
        if not request.form.get('dN'):
            return "1"
        file_hash=hasher.hexdigest()
        data = uploadSuccess(unique_id,file_hash)
        mediaHash.pop(unique_id)
        if data:
            return [data,file_hash]
        return "0"

    name=str(request.form['name'])
    typ=str(request.form['typ'])
    curr=str(request.form['server'])
    chunk=request.files['chunk'].read()
    unique_id = str(uuid.uuid4())
    with open("media/"+ unique_id ,"wb") as file:
        file.write(chunk)
    hasher=hashlib.sha256()
    hasher.update(chunk)
    mediaHash[unique_id]=[hasher,name,typ,curr]  #store name,typ,hasher in List :
    if request.form.get('dN'):
        file_hash=hasher.hexdigest()
        data = uploadSuccess(unique_id,file_hash)
        mediaHash.pop(unique_id)
        if data:
            return [data,file_hash]
        return "0"
    return unique_id
@app.route("/channels",methods=["GET"])
def channel_chat():
    if not session.get("name"):
        return redirect("/login")
    name=session.get("name")
    myserver=session.get("myserver")
    curr=session.get("server")
    id=session.get(curr)
    return render_template("channel_chat.html",name=name,id=id,server=curr,myservers=myserver)
@app.route('/download/<server>',methods=["GET"])
def download_database(server):
    if app.config['SQLALCHEMY_BINDS'].get(str(server)):
        path =str(app.config['SQLALCHEMY_BINDS'][str(server)]).rsplit("///")[1]
        return send_file(path, as_attachment=True)
    else:
        return make_response('Not Found',404)
if __name__ == '__main__':
    socketio.run(app)
# TODO:
    # Allow user to customise their server        -- Trying to figure out
    # Make it fast 
    #   -- 1. use the dictionary to check for channesl instead of checking database.
    #   -- 2. If i can rewrite loginlogic func again.

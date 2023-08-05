import os, uuid, asyncio, mimetypes, hashlib , datetime, pytz, json, time
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
    id=db.Column(db.Integer,primary_key=True)                            #User ID
    username=db.Column(db.String, unique=True, nullable=False)       #user name
    password=db.Column(db.String, nullable=False)                    #user password
    description=db.Column(db.String, nullable=True)
class channel(Base):
    __tablename__="channel"
    id=db.Column(db.Integer,primary_key=True)                   #topic ID
    name=db.Column(db.String, nullable=False)                   #topic name
    creator_id=db.Column(db.Integer,db.ForeignKey('users.id'))  #creator ID
    description=db.Column(db.String, nullable=True)
    user=db.relationship('users')
class chats(Base):
    __tablename__="chats"
    id=db.Column(db.Integer,primary_key=True)
    key=db.Column(db.String,nullable=False)                                 #Private Key
    data=db.Column(db.String, nullable=False)                               #actuall msg
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
Tables={"app":{}}
room_dict={"app":{"/":{}}}
inspector = inspect(engine)
tbls = inspector.get_table_names()
for tb in tbls:
    if tb.isdigit():
        Tables["app"][int(tb)]=create_channel(tb, Base,users)
        room_dict["app"].update({int(tb):{}})
Base.metadata.create_all(bind=engine)
sqlsession=sessionmaker(bind=engine)
app.config["SESSION_PERMANENT"]=False
app.config["SESSION_TYPE"]="filesystem"
Session(app)
engine={"app":engine}
server={"app":sqlsession()}
base={"app":Base}
mediaHash={}
def private_key(a,b):
    if a<=b:
        key=str(a)+"-"+str(b)
    else:
        key=str(b)+"-"+str(a)
    return hashlib.md5(key.encode()).hexdigest()
uploads_dir = os.path.join('db')
if not os.path.exists(os.path.join("media")):
    os.makedirs(os.path.join("media"))
if not os.path.exists(os.path.join("db")):
    os.makedirs(os.path.join("db"))
@app.route('/create',methods=["POST"])
def createdb():
    name=str(request.form.get("name"))
    if name in server or "/" in name:
        return render_template("message.html",msg="select a unique and valid name.",goto="/")
    db_uri = f'sqlite:///db/{name}.sqlite3'
    Engine = create_engine(db_uri)
    Engine.connect()
    engine[name]=Engine
    metadata=MetaData(bind=Engine)
    Base=declarative_base(metadata=metadata)
    req=["users","channel","chats","media"]
    Tables[name]={}
    for table_name in req:
        table = base["app"].metadata.tables.get(table_name)
        table.tometadata(metadata)
    class users(Base):
        __tablename__ = "users"
        __table_args__ = {"extend_existing": True}
        id = Column(db.Integer, primary_key=True)  
        username = Column(db.String(20), unique=True, nullable=False) 
        password = Column(db.String(30), nullable=False)
    Base.metadata.create_all(bind=Engine)
    app.config['SQLALCHEMY_BINDS'][name]=db_uri
    base[name]=Base
    Session=sessionmaker(bind=Engine)
    server[name]=Session()
    room_dict[name]={
        "/":{}
    }
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
            Tables[name]={}
            room_dict[name]={
                "/":{}
            }
            class users(Base):
                __tablename__ = "users"
                __table_args__ = {"extend_existing": True}
                id = Column(db.Integer, primary_key=True)  
                username = Column(db.String(20), unique=True, nullable=False) 
                password = Column(db.String(30), nullable=False)
            Base.metadata.create_all(bind=Engine)
            inspector = inspect(Engine)
            tbls = inspector.get_table_names()
            for tb in tbls:
                if tb.isdigit():
                    Tables[name][int(tb)]=create_channel(tb, Base,users)
                    room_dict[name].update({int(tb):{}})
            Base.metadata.create_all(bind=Engine)
            base[name]=Base
            engine[name]=Engine
            Session=sessionmaker(bind=Engine)
            server[name]=Session()
        except:
            app.config['SQLALCHEMY_BINDS'].pop(name,None)
            os.remove("db/"+name+".sqlite3")
            server.pop(name,None)
            session.clear()
            return render_template("message.html",msg="NOT A VALID DATABASE",goto="/login")
        # UPDATING ROOM_DICT WITH NEW SERVER
        session.clear()
    return redirect("/login")
#  WHEN HAVE TO DELETE THE SERVER(not up-to-date)

    # try:
    #     deldb=request.form['deldb']
    # except:
    #     deldb=False
    # if deldb:
    #     os.remove("db/"+str(deldb).rsplit("-")[1])
    #     app.config['SQLALCHEMY_DATABASE_URI'] ="sqlite:///db.sqlite3"
    #     return redirect("/servers")
@socketio.on('disconnect')
def on_disconnect():
    changeServer(False)
@socketio.on('Load')
def Load():
    curr=session.get('server')
    join_room(curr)
    room_dict[curr]["/"].update({session.get("name"):request.sid})
    socketio.emit("serverlive",room_dict[curr]["/"],room=curr)
    Media=server[curr].query(media).all()
    Md=[[media.id,media.hash,media.name] for media in Media]
    socketio.emit("medias",Md,to=request.sid)
@socketio.on("changeServer")
def changeServer(newServer):
    # REMOVE PREV 
    change(False)
    oldServer=session.get("server")
    if oldServer:
        leave_room(oldServer)
        if room_dict[oldServer]["/"].pop(session.get("name"),None):
            socketio.emit("serverlive",room_dict[oldServer]["/"],room=oldServer)
    if newServer:
        channels=server[newServer].query(channel).all()
        session["server"]=newServer
        join_room(newServer)
        room_dict[newServer]["/"].update({session.get("name"):request.sid})
        socketio.emit("serverlive",room_dict[newServer]["/"],room=newServer)
        channel_list=[session.get("server")]
        channel_list.append([[channel.id,channel.name,channel.user.username] for channel in channels])
        socketio.emit("showNewServer",channel_list,to=request.sid)    
        Media=server[newServer].query(media).all()
        Md=[[media.id,media.hash,media.name] for media in Media]
        socketio.emit("medias",Md,to=request.sid)
@socketio.on("create")
def create(newchannel):
    curr=session.get("server")
    id=session.get(curr)
    Topic=channel(name=newchannel,creator_id=id)
    server[curr].add(Topic)
    server[curr].commit()
    Base=base[curr]
    Tables[curr][Topic.id]=create_channel(Topic.id, Base,users)
    Base.metadata.create_all(engine[curr])
    room_dict[curr][Topic.id]={}
    new={"channel":[Topic.id,Topic.name,Topic.user.username]}
    socketio.emit("show_this",new,room=curr)
@socketio.on("search_text")
def search(text):
    curr=session.get("server")
    user_list=server[curr].query(users).filter(users.username.like("%"+text+"%")).all()
    Users={"users":[user.username for user in user_list]}
    socketio.emit("show_this",Users,to=request.sid)
@socketio.on("change")
def change(To):
    # IDENTIFY
    curr = session.get("server")
    name = session.get("name")
    id = session.get(curr)
    # CLEAR PREV IF ANY AND NOTIFY THAT ROOM
    prev = session.get('channel')
    if not prev:
        prev=session.get("key")
        session["key"]=None
        session["friend"]=None
    session["channel"]=None
    if prev:
        leave_room(curr+str(prev))
        if room_dict[curr][prev].pop(name,None):
            socketio.emit("notify",room_dict[curr][prev],room=curr+str(prev))

    # CLEAR
    if not To:
        return 
    # GOTO CHANNEL/FRND IF ANY
    if "channel" in To:
        to=int(To["channel"])
        # current_channel=server[curr].query(channel).filter_by(name=to).first()
        session["channel"]=to
        last_msgs=server[curr].query(Tables[curr][to]).order_by(Tables[curr][to].id.desc()).limit(30)
        room_dict[curr][to].update({name:1})
    if "Frnd" in To:
        to=To["Frnd"]
        frnd=server[curr].query(users).filter_by(username=to).first()
        if not frnd:
            return render_template("message.html",msg="user doesn't exist",goto="/channels")
        to=private_key(id,frnd.id)
        session["key"]=to
        if frnd.id<=id:
            me=True
        else:
            me=False
        session["bool"]=me
        session["friend"]=frnd.username
        last_msgs=server[curr].query(chats).order_by(chats.id.desc()).filter_by(key=to).limit(30)
        if to in room_dict[curr]:
            room_dict[curr][to].update({name:1})
        else:
            room_dict[curr].update({to:{name:1}})
    # JOIN ROOM AND NOTIFY
    to=to
    join_room(curr+str(to))
    socketio.emit("notify",room_dict[curr][to],to=curr+str(to))
    # ARRANGE MSGS IN A FORMAT
    
    if session.get("channel"):
        Msgs=[[msg.user.username,msg.id,msg.data] for msg in last_msgs]
        Msgs.append(None)
    else:
        Msgs=[[msg.id,msg.data] for msg in last_msgs]
        Msgs.append(me)
    if len(Msgs)!=31:
        Msgs.append(0)
        session["history"]=0
    else:
        Msgs.append(1)
        session["history"]=1
    socketio.emit('showMessages',Msgs,to=request.sid)     
@socketio.on('message')
def handel_message(message):
    msg={}
    if message.get('0'):
        msg[0]=message.get('0')
    curr=session.get("server")
    if message.get('1'):
        medea=server[curr].query(media).filter_by(id=message.get('1')).first()
        if medea==None:
            return
        msg[1]=message.get('1')
    id=session.get(curr)
    name=session.get("name")
    channel_id=session.get("channel")
    msg[3]=datetime.datetime.now(india_timezone).strftime('%d-%m-%Y %H:%M:%S')
    # FOR CHANNEL
    if channel_id:
        if message.get('2'):
            reply=server[curr].query(Tables[curr][channel_id]).filter_by(id=int(message.get('2'))).first()
            if reply==None:
                return
            msg[2]=message.get('2')
        msg=json.dumps(msg)
        message=Tables[curr][channel_id](data=msg,sender_id=id)
        server[curr].add(message)
        server[curr].commit()
        socketio.emit('show_message',[name,message.id,msg], room = curr+str(channel_id))
        for srvr in room_dict.keys():
            if srvr==curr:
                for usr in room_dict[srvr]["/"].keys():
                    if usr not in room_dict[srvr][channel_id].keys():    
                        socketio.emit('currupdate',channel_id,to=room_dict[curr]["/"][usr])
            else:
                for usr in room_dict[srvr]["/"].keys():
                    socketio.emit('otherupdate',curr,to=room_dict[srvr]["/"][usr])
    # FOR DM's
    else:
        key=session.get("key")
        if message.get('2'):
            reply=server[curr].query(chats).filter_by(id=int(message.get("2"))).first()
            if reply==None or reply.key!=key:
                return
            msg[2]=message.get('2')
        msg[5]=session.get('bool')
        msg=json.dumps(msg)
        message=chats(data=msg,key=key)
        server[curr].add(message)
        server[curr].commit()
        socketio.emit('show_message',[message.id,msg], room = curr+key)
        if len(room_dict[curr][key])==1 and not session.get("friend")==name:
            for srvr in room_dict.keys():
                if srvr==curr:
                    usr = room_dict[srvr]["/"].get(session.get("friend"))
                    if usr!=None:
                        socketio.emit('dm',[name],to=usr)
                else:
                    usr = room_dict[srvr]["/"].get(session.get("friend"))
                    if usr!=None:
                        socketio.emit('otherupdate',curr,to=usr)
                        return 
@socketio.on('reaction')
def reaction(reactData):
    curr=session.get("server")
    id=session.get(curr)
    channel_id=session.get("channel")
    # FOR CHANNEL
    if channel_id:
        msg=server[curr].query(Tables[curr][channel_id]).filter_by(id=reactData[0]).first()
        if msg:
            message=json.loads(msg.data)
            if reactData[1]:
                if message.get('4'):
                    message['4'][str(id)]=reactData[1]
                else:
                    message['4']={str(id):reactData[1]}
            else:
                message['4'].pop(str(id))
            data=json.dumps(message)
            msg.data=data
            server[curr].commit()
            socketio.emit('reaction',[reactData[0],id,reactData[1]],to=curr+str(channel_id))
    # FOR PRVT
    else:
        msg=server[curr].query(chats).filter_by(key=session.get('key')).first()
        if msg:
            message=json.loads(msg.data)
            if reactData[1]:
                if message.get('4'):
                    message['4'][str(id)]=reactData[1]
                else:
                    message['4']={str(id):reactData[1]}
            else:
                message['4'].pop(str(id))
            data=json.dumps(message)
            msg.data=data
            server[curr].commit()
            socketio.emit('reaction',[reactData[0],id,reactData[1]],to=curr+session.get('key'))
@socketio.on('getHistory')
def getHistory():
    curr=session.get("server")
    # id=session.get('id')
    history=session.get("history")
    channel_id=int(session.get("channel"))
    times=session.get("history")
    if channel_id:
        last_msgs=server[curr].query(Tables[curr][channel_id]).order_by(Tables[curr][channel_id].id.desc()).offset(30*times).limit(30)
        Msgs=[[msg.user.username,msg.id,msg.data] for msg in last_msgs]
        Msgs.append(None)
    else:
        last_msgs=server[curr].query(chats).order_by(chats.id.desc()).filter(and_(chats.id<postID,chats.key==session.get("key"))).limit(30)
        Msgs=[[msg.id,msg.data] for msg in last_msgs]
        Msgs.append(me)
    session["history"]+=1
    if len(Msgs)!=31:
        Msgs.append(0)
    else:
        Msgs.append(1)
    socketio.emit('showMessages',Msgs,to=request.sid)
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
@app.route("/media/<id>",methods=["GET"])
def handel_get_Media(id):
    srvr=session.get('server')
    if not srvr:
        return "0"
    Media=server[srvr].query(media).filter_by(id=id).first()
    if Media != None:
        # ext=mimetypes.guess_extension(json.loads(Media.name)[1])
        # if ext == None:
        #     ext=""
        file_path="media/"+Media.hash
        if os.path.exists(file_path):
            return send_file(file_path) #if this doesnt work put mimetype = (binary)
        else:
            return make_response('Not found',404)
    else:
        return make_response('Not found',404)
@app.route("/media",methods=["POST"])
def handel_media():
    def uploadSuccess(unique_id,file_hash,curr):
        session=server[curr]
        check=session.query(media).filter_by(hash=file_hash).first()
        if check==None:
            data=mediaHash[unique_id]
            name=[data[1],data[2]] #store only name & typ 
            Media=media(hash=file_hash,name=json.dumps(name))
            session.add(Media)
            session.commit()
            os.rename("media/"+unique_id,"media/"+file_hash) #file uploaded
            socketio.emit("media",[Media.id,Media.hash,name],room=curr)
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
        curr = session.get("server")
        data = uploadSuccess(unique_id,file_hash,curr)
        mediaHash.pop(unique_id)
        if data:
            return [data,file_hash]
        return "0"

    name=str(request.form['name'])
    typ=str(request.form['typ'])
    chunk=request.files['chunk'].read()
    unique_id = str(uuid.uuid4())
    with open("media/"+ unique_id ,"wb") as file:
        file.write(chunk)
    hasher=hashlib.sha256()
    hasher.update(chunk)
    mediaHash[unique_id]=[hasher,name,typ]  #store name,typ,hasher in List :
    if request.form.get('dN'):
        file_hash=hasher.hexdigest()
        curr = session.get("server")
        data = uploadSuccess(unique_id,file_hash,curr)
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
    channels=server[curr].query(channel).all()
    return render_template("channel_chat.html",name=name,id=id,server=curr,mysrvr=myserver,channels=channels)  
@app.route('/download/<server>',methods=["GET"])
def download_database(server):
    if server and app.config['SQLALCHEMY_BINDS'].get(str(server)):
        path =str(app.config['SQLALCHEMY_BINDS'][str(server)]).rsplit("///")[1]
        return send_file(path, as_attachment=True)
    else:
        return make_response('Not Found',404)
if __name__ == '__main__':
    socketio.run(app)

# TODO:
    # Add Media Id and use that instead of hash
    # Streaming of media when asked
    # Update chunksize acc.to internet speed
    # Send all the chats on load 
    # Add browser storage for quick response and maintainse
    # (learning how to deal with tampering attacks)
    # Use reddis db for storing peoples who are online
    # this is commited because streak wont increase after commit on IndexedDB branch
    # this too is a commit for streak i created a system where users can get/store
    # all messages they may use into indexedDB 

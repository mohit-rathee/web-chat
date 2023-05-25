import os
from flask import Flask, render_template, request, redirect, session
from werkzeug.utils import secure_filename
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
from sqlalchemy.sql import func
from flask import send_file
from passlib.hash import sha256_crypt
import hashlib 
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy import create_engine, MetaData, Column, func, text, Table, String
from sqlalchemy.ext.declarative import declared_attr
from flask_socketio import SocketIO, join_room, emit, leave_room,send
import gevent
from pytz import timezone


app = Flask(__name__)
app.debug=True
app.config.from_object(__name__)
socketio = SocketIO(app, async_mode='gevent', transport=['websocket'])
app.config['SECRET_KEY'] ="!!!"  #os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] ="sqlite:///test.sqlite3"   #os.environ.get('DATABASE_URI')
app.config.update(
    SESSION_COOKIE_SAMESITE='None',
    SESSION_COOKIE_SECURE='True',
    SQLALCHEMY_TRACK_MODIFICATIONS='False'
)
app.config['SQLALCHEMY_BINDS']={}
db = SQLAlchemy(app)

class users(db.Model):
    id=db.Column(db.Integer,primary_key=True)                            #User ID
    username=db.Column(db.String(20), unique=True, nullable=False)       #user name
    password=db.Column(db.String(30), nullable=False)                    #user password
    balance=db.Column(db.Integer, nullable=True, default=0)              #user balance
    topic=db.relationship('channel',backref='user')
    chat=db.relationship('chats',backref='user')
    # short_message=db.relationship('short_messages',backref='sender')
    # short_post=db.relationship('short_posts',backref='sender')
    def __init__(self, username, password, balance):
        self.username=username
        self.password=password
        self.balance=balance

class channel(db.Model):
    id=db.Column(db.Integer,primary_key=True)                   #topic ID
    name=db.Column(db.String, nullable=False,unique=True)       #topic name
    creator_id=db.Column(db.Integer,db.ForeignKey('users.id'))  #creator ID

class chats(db.Model):
    id=db.Column(db.Integer,primary_key=True)                               #topic ID
    key=db.Column(db.String,nullable=False)                                 #Private Key
    sender_id= db.Column(db.Integer, db.ForeignKey('users.id'))             #Sender ID
    data=db.Column(db.String, nullable=False)                               #actuall msg
    time = db.Column(db.DateTime, default=func.now(timezone('Asia/Kolkata')))#time
 
# class posts(db.Model):
#     __abstract__ = True
#     id = db.Column(db.Integer, primary_key=True)
#     data = db.Column(db.String, nullable=False)
#     # sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
#     time = db.Column(db.DateTime, server_default=func.now(timezone('Asia/Kolkata')))
#     @declared_attr
#     def post_id(cls):
#         return Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
#     user=db.relationship('users')



# class short_messages(db.Model):
#     id=db.Column(db.Integer,primary_key=True)                                #msg/post ID
#     key=db.Column(db.String,nullable=False)                                  #Private Key
#     data=db.Column(db.String, nullable=False)                                #actuall msg
#     sender_id= db.Column(db.Integer, db.ForeignKey('users.id'))              #User ID
#     time = db.Column(db.DateTime, default=func.now(timezone('Asia/Kolkata'))) 

# class short_posts(db.Model):
#     id=db.Column(db.Integer,primary_key=True)                                #msg/post ID
#     data=db.Column(db.String, nullable=False)                                #actuall msg
#     sender_id= db.Column(db.Integer, db.ForeignKey('users.id'))              #User ID
#     topic_id=db.Column(db.Integer, db.ForeignKey('channel.id')) 
#     time = db.Column(db.DateTime, default=func.now(timezone('Asia/Kolkata'))) 




# SQLALCHEMY_TRACK_MODIFICATIONS = True

db.create_all()


#Session
app.config["SESSION_PERMANENT"]=False
app.config["SESSION_TYPE"]="filesystem"
Session(app)

# SAVING APP's SESSION OBJECT INTO DICTIONARY
room_dict={
    # "/":{}, i think will use room_dict[#server]["/"] to get everyone 
    #         so i don't have to store them in multiple places places
    "app":{
        "/":{}
        }
    }
server={
    "app":db.session
}
engine={
    "app":db.engine
}
base={
    "app":db.Model
}
Tables={
    # models of channels
}


# FOR DEVELOPMENT ONLY
Engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
metadata=MetaData()
metadata.reflect(Engine)
Base=automap_base(metadata=metadata)
Base.prepare()
Session=sessionmaker(bind=Engine)
server["app"]=Session()
engine["app"]=Engine
tables=server["app"].query(channel).all()
room_dict["app"]={'/':{}}
for tb in tables:
    try:
        tab = Base.classes[tb.name]
        setattr(tab, 'user', relationship('users'))
        # Base.prepare()
        Tables[tb.name]=tab
        room_dict["app"].update({tb.name:{}})
    except:
        continue
base["app"]=Base

@app.route('/upload',methods=["POST"])
def upload_db():
    files=request.files.getlist('files')
    for file in files:
        if file and file.filename.split(".")[1]=="sqlite3":
            uploads_dir = os.path.join('db')
            if os.path.exists(uploads_dir)==False:
                os.makedirs(uploads_dir)
            file.save(os.path.join(uploads_dir,secure_filename(file.filename))) 
            data=secure_filename(file.filename).split(".")[0]
            app.config['SQLALCHEMY_BINDS'][data] ="sqlite:///"+str(os.path.join(uploads_dir,secure_filename(file.filename)))
            # CREATE AN ENGINE, GET METADATA, USE AUTOMAP TO MAP TABLES CREATE A SESSION()
            # SAVES THE SESSION OBJECT IN A DICTIONARY
            try:
                Engine = create_engine(app.config['SQLALCHEMY_BINDS'][str(data)])
                metadata=MetaData()
                metadata.reflect(Engine)
                Base=automap_base(metadata=metadata)
                Base.prepare()
                Session=sessionmaker(bind=Engine)
                server[data]=Session()
                engine[data]=Engine
                tables=server[data].query(channel).all()
                room_dict[data]={'/':{}}
                for tb in tables:
                    try:
                        tab = Base.classes[tb.name]
                        setattr(tab, 'user', relationship('users'))
                        # Base.prepare()
                        Tables[tb.name]=tab
                        room_dict[data].update({tb.name:{}})
                    except:
                        continue
                base[data]=Base
            except:
                app.config['SQLALCHEMY_BINDS'].pop(data,None)
                os.remove("db/"+data+".sqlite3")
                server.pop(data,None)
                return render_template("message.html",msg="NOT A VALID DATABASE",goto="/servers")
            # UPDATING ROOM_DICT WITH NEW SERVER
            session.clear()

                
        else:
            return render_template("message.html",msg="select a valid database file (*.sqlite3)",goto="/servers")
    return redirect("/servers")

@app.route('/servers',methods=["GET","POST"])
def change_db():
    # REDIRECT TO APP IF LOGGED IN
    if request.method=="GET":
        if session.get("name"):
            return redirect("/channels")
    # SHOW "/SERVERS"
    session.clear()
    if os.path.exists("db")==False:
        os.makedirs("db")
    databases=[]
    for db in os.listdir("db"):
        databases.append(db.split(".")[0]) 
    return render_template("database.html",databases=databases)

#  WHEN HAVE TO DELETE THE SERVER(not up-to-date)

    # try:
    #     deldb=request.form['deldb']
    # except:
    #     deldb=False
    # if deldb:
    #     os.remove("db/"+str(deldb).rsplit("-")[1])
    #     app.config['SQLALCHEMY_DATABASE_URI'] ="sqlite:///db.sqlite3"
    #     return redirect("/servers")

# @app.after_request
# def add_header(response):
#     response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
#     response.headers['Pragma'] = 'no-cache'
#     response.headers['Expires'] = '0'
#     response.headers['Cache-Control'] = 'public, max-age=0'
#     # response.headers['Last-Modified'] = DateTime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
#     return response
@socketio.on('disconnect')
def on_disconnect():
    changeServer(False)

@socketio.on('Load')
def Load():
    curr=session.get('server')
    join_room(curr)
    room_dict[curr]["/"].update({session.get("name"):request.sid})
    socketio.emit("serverlive",room_dict[curr]["/"],room=curr)

@socketio.on("changeServer")
def changeServer(newServer):
    # REMOVE PREV 
    change(False)
    oldServer=session.get("server")
    if oldServer:
        # print(socketio.server.manager.rooms)
        leave_room(oldServer)
        # print("after leaving")
        # print(socketio.server.manager.rooms)
        if room_dict[oldServer]["/"].pop(session.get("name"),None):
            socketio.emit("serverlive",room_dict[oldServer]["/"],room=oldServer)
    # GOTO NEWSERVER IF ANY ELSE LOGOUT
    if newServer:
        # print("joining new server")
        channels=server[newServer].query(channel).all()
        session["server"]=newServer
        join_room(newServer)
        # print(socketio.server.manager.rooms)
        room_dict[newServer]["/"].update({session.get("name"):request.sid})
        socketio.emit("serverlive",room_dict[newServer]["/"],room=newServer)
        channel_list=[session.get("server")]
        channel_list.append([[channel.name,channel.user.username] for channel in channels])
        socketio.emit("showNewServer",channel_list,to=request.sid)    
    else:
        session.clear()
        session["name"]=None
        socketio.emit("Logout",to=request.sid)

@socketio.on("create")
def create(newchannel):
    curr=session.get("server")
    id=session.get(curr)
    Topic=channel(name=newchannel,creator_id=id)
    server[curr].add(Topic)
    try:
        server[curr].commit()
    except IntegrityError:
        return
    Base=base[curr]

    class Channel(Base):
        __tablename__ = newchannel
        id = db.Column(db.Integer, primary_key=True)
        data = db.Column(db.String, nullable=False)
        sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
        time = db.Column(db.DateTime, server_default=func.now())
        # user = db.relationship('users')  

    Base.metadata.create_all(engine[curr])
    # Base.prepare(engine[curr], reflect=True)
    # print(Base.metadata.tables)
    # print(Channel)
    # base[curr]=Base

# Channel = Table(
#     newchannel,
#     Base.metadata,
#     Column('id', Integer, primary_key=True),
#     Column('data', String, nullable=False),
#     Column('sender_id', Integer, ForeignKey('users.id')),
#     Column('time', DateTime, server_default=func.now(timezone('Asia/Kolkata'))),
# )

    # print(base[curr].metadata)
    metadata=MetaData()
    metadata.reflect(engine[curr])
    Base=automap_base(metadata=metadata)
    Base.prepare()
    NEWChannel=Base.classes[newchannel]
    setattr(NEWChannel, 'user', relationship('users'))
    Tables.update({newchannel:NEWChannel})
    base[curr]=Base
    room_dict[curr][newchannel]={}
    new={"channel":{Topic.name:Topic.user.username}}
    socketio.emit("show_this",new,room=curr)
    # print(Tables)


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
        leave_room(curr+prev)
        if room_dict[curr][prev].pop(name,None):
            socketio.emit("notify",room_dict[curr][prev],room=curr+prev)

    # CLEAR
    if not To:
        return 
    # GOTO CHANNEL/FRND IF ANY
    if "channel" in To:
        to=To["channel"]
        # current_channel=server[curr].query(channel).filter_by(name=to).first()
        session["channel"]=to
        # print(Tables)
        last_msgs=server[curr].query(Tables[to]).order_by(Tables[to].id.desc()).limit(30)
        room_dict[curr][to].update({name:1})
    if "Frnd" in To:
        to=To["Frnd"]
        frnd=server[curr].query(users).filter_by(username=to).first()
        if not frnd:
            return 
        to=private_key(id,frnd.id)
        session["key"]=to
        session["friend"]=frnd.username
        last_msgs=server[curr].query(chats).order_by(chats.id.desc()).filter_by(key=to).limit(30)
        if to in room_dict[curr]:
            room_dict[curr][to].update({name:1})
        else:
            room_dict[curr].update({to:{name:1}})
    # JOIN ROOM AND NOTIFY
    join_room(curr+to)
    socketio.emit("notify",room_dict[curr][to],to=curr+to)
    # ARRANGE MSGS IN A FORMAT
    Msgs=[]
    for msg in last_msgs:
        Msgs.append([msg.user.username,msg.data,msg.time.strftime("%D  %H:%M")])
    if len(Msgs)!=30:
        Msgs.append(0)
        session["history"]=0
    else:
        Msgs.append(1)
        session["history"]=1
    socketio.emit('showMessages',Msgs,to=request.sid)


@socketio.on('recieve_message')
def handel_recieve_message(data):
    # IDENTIFY
    curr=session.get("server")
    name=session.get("name")
    id=session.get(curr)
    channel_name=session.get("channel")
    key=session.get("key")
    # FOR CHANNEL
    if channel_name:
        # current_channel=server[curr].query(channel).filter_by(name=channel_name).first()
        msg=Tables[channel_name](data=data,sender_id=id)
        server[curr].add(msg)
        server[curr].commit()
        socketio.emit('show_message',[name,data,msg.time.strftime("%D  %H:%M")], room = curr+channel_name)
        for srvr in room_dict.keys():
            if srvr==curr:
                for usr in room_dict[srvr]["/"].keys():
                    if usr not in room_dict[srvr][channel_name].keys():    
                        socketio.emit('currupdate',channel_name,to=room_dict[curr]["/"][usr])
            else:
                for usr in room_dict[srvr]["/"].keys():
                    socketio.emit('otherupdate',curr,to=room_dict[srvr]["/"][usr])
    # FOR DM's
    else:
        msg=chats(data=data,key=key,sender_id=id)
        server[curr].add(msg)
        server[curr].commit()
        socketio.emit('show_message',[name,data,msg.time.strftime("%D  %H:%M")], room = curr+key)
        if len(room_dict[curr][key])==1 and not session.get("friend")==name:
            for srvr in room_dict.keys():
                if srvr==curr:
                    for usr in room_dict[srvr]["/"]:
                        if usr == session.get("friend"):
                            socketio.emit('dm',[name],to=room_dict[srvr]["/"][usr])
                else:
                    for usr in room_dict[srvr]["/"]:
                        if usr == session.get('friend'):
                            socketio.emit('otherupdate',curr,to=room_dict[srvr]["/"][usr])
            

@socketio.on('getHistory')
def getHistory():
    curr=session.get("server")
    # id=session.get('id')
    history=session.get("history")
    channel_name=session.get("channel")
    times=session.get("history")
    if channel_name:
        # current_channel=server[curr].query(channel).filter_by(name=channel_name).first()
        last_msgs=server[curr].query(Tables[channel_name]).order_by(Tables[channel_name].id.desc()).offset(30*times).limit(30)
    else:
        last_msgs=server[curr].query(chats).order_by(chats.id.desc()).filter(and_(chats.id<postID,chats.key==session.get("key"))).limit(30)
    Msgs=[]
    for msg in last_msgs:
        Msgs.append([msg.user.username,msg.data,msg.time.strftime("%D  %H:%M")])
    session["history"]+=1
    if len(Msgs)!=30:
        Msgs.append(0)
    else:
        Msgs.append(1)
    socketio.emit('showMessages',Msgs,to=request.sid)
    
    
@app.route('/',methods=["GET","POST"])
def index():
    if session.get("name")==None:
        return redirect("/servers")
    else:
        return redirect("/channels")


# OBJECTIVE ==>  PASSWORD IN EVERY DATABASE SHOULD BE SAME 
#                USE MINIMUM CALCULATION TO AUTHENTICATE
# little challenge ==>   UNDERSTAND login/signup PROCESS YOURSELF 

def loginlogic(name,password):
    myServer=session.get("myserver")
    pswdHash=None
    if myServer!=None:
        session["server"]=myServer[0]
        user=server[myServer[0]].query(users).filter_by(id=session.get(myServer[0])).first()
        pswdHash=user.password
    else:
        myServer=[]
    done=[]
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
                            done.append(srvr)
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
        done.append(srvr)
    session["myserver"]=myServer[:]
    if done:
        return True
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
                    user=users(username=name,password=pswdHash,balance=0)
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



@app.route("/channels",methods=["GET"])
def channel_chat():
    if not session.get("name"):
        return redirect("/servers")
    name=session.get("name")
    myserver=session.get("myserver")
    curr=myserver[0]
    channels=server[curr].query(channel).all()
    ppls=room_dict[curr]["/"]
    print(ppls)
    peoples=[[people] for people in ppls]
    print(peoples)
    return render_template("channel_chat.html",name=name,server=curr,mysrvr=myserver,channels=channels,peoples=peoples)
    
                


#private key
def private_key(a,b):
    a=int(a)
    b=int(b)
    if a<=b:
        key=str(a)+"-"+str(b)
    else:
        key=str(b)+"-"+str(a)
    return hashlib.md5(key.encode()).hexdigest()


@app.route('/download/<server>')
def download_database(server):
    if server=="app":
        path= str(app.config['SQLALCHEMY_DATABASE_URI']).rsplit("///")[1]
    else:
        path =str(app.config['SQLALCHEMY_BINDS'][str(server)]).rsplit("///")[1]
    return send_file(path, as_attachment=True)



if __name__ == '__main__':
    socketio.run(app)
    # app.run()

# ---^---   /====      /--------' ---^---
#    |     /====     /------/        |
#    |    /====  ,-------/           |
# @app.route("/test")
# def test():
#     return render_template("webRTC.html")

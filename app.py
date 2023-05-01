import os
from flask import Flask, render_template, request, redirect, session
from werkzeug.utils import secure_filename
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
from datetime import timezone
from sqlalchemy.sql import func
from flask import send_file
from passlib.hash import sha256_crypt
import hashlib 
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine, MetaData, Column
from flask_socketio import SocketIO, join_room, emit, leave_room,send
import gevent


app = Flask(__name__)
app.config.from_object(__name__)
socketio = SocketIO(app, async_mode='gevent', transport=['websocket'])
app.config['SECRET_KEY'] ="alsdkjfoldsjoidsvjoismoid479583749583405934085039"  #os.environ.get('SECRET_KEY')
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
    post=db.relationship('posts',backref='user')                         #relation#
    topic=db.relationship('channel',backref='user')
    chat=db.relationship('chats',backref='user')
    short_message=db.relationship('short_messages',backref='sender')
    short_post=db.relationship('short_posts',backref='sender')
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
    time = db.Column(db.DateTime, default=func.now())                       #time

class posts(db.Model):
    id=db.Column(db.Integer,primary_key=True)                               #msg/post ID
    data=db.Column(db.String, nullable=False)                               #actuall msg
    sender_id= db.Column(db.Integer, db.ForeignKey('users.id'))             #User ID
    time = db.Column(db.DateTime, default=func.now())                       #time
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'))

class short_messages(db.Model):
    id=db.Column(db.Integer,primary_key=True)                                #msg/post ID
    key=db.Column(db.String,nullable=False)                                  #Private Key
    data=db.Column(db.String, nullable=False)                                #actuall msg
    sender_id= db.Column(db.Integer, db.ForeignKey('users.id'))              #User ID
    time = db.Column(db.DateTime, default=func.now()) 

class short_posts(db.Model):
    id=db.Column(db.Integer,primary_key=True)                                #msg/post ID
    data=db.Column(db.String, nullable=False)                                #actuall msg
    sender_id= db.Column(db.Integer, db.ForeignKey('users.id'))              #User ID
    topic_id=db.Column(db.Integer, db.ForeignKey('channel.id')) 
    time = db.Column(db.DateTime, default=func.now()) 




# SQLALCHEMY_TRACK_MODIFICATIONS = True

db.create_all()


#Session
app.config["SESSION_PERMANENT"]=False
app.config["SESSION_TYPE"]="filesystem"
Session(app)

room_dict={"app":{"/":[]}}
server={
    "app":db.session,
}


# Routes
# @app.before_request
# def hello():
#     print(request.path+"/"+request.method)


# @app.teardown_request
# def teardown_request(exception):
#     print("done")
# allowedExtention=("sqlite3")
# def allowed(filename):
#     return '.'in filename and filename.rsplit('.',1)(1).lower() in allowedExtention

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
            Engine = create_engine(app.config['SQLALCHEMY_BINDS'][str(data)])
            metadata=MetaData()
            metadata.reflect(Engine)
            Base=automap_base(metadata=metadata)
            Base.prepare()
            Session=sessionmaker(bind=Engine)
            server[data]=Session()
            session.clear()
            room_dict[data]={"/":[]}
        else:
            return render_template("message.html",msg="select a valid database file or rename it except db.sqlite3.",goto="/servers")
    return redirect("/servers")

@app.route('/servers',methods=["GET","POST"])
def change_db():
    if request.method=="GET":
        if session.get("name"):
            return redirect("/channels")
    session.clear()
    if os.path.exists("db")==False:
        os.makedirs("db")
    databases=[]
    for db in os.listdir("db"):
        databases.append(db.split(".")[0]) 
    session["server"]=None
    session["name"]=None
    session["channel"]=None
    return render_template("database.html",databases=databases)
    # try:
    #     deldb=request.form['deldb']
    # except:
    #     deldb=False
    # if deldb:
    #     os.remove("db/"+str(deldb).rsplit("-")[1])
    #     app.config['SQLALCHEMY_DATABASE_URI'] ="sqlite:///db.sqlite3"
    #     return redirect("/servers")

@socketio.on("changeServer")
def changeServer(newServer):
    oldServer=session.get("server")
    if oldServer:
        leave_room(oldServer)
        if session.get("name") in room_dict[oldServer]["/"]:
            room_dict[oldServer]["/"].remove(session.get("name"))
            socketio.emit("serverlive",room_dict[oldServer]["/"],room=oldServer)
    if newServer:
        try:
            channels=server[newServer].query(channel).all()
            # channel_list=[newServer]
        except:
            socketio.emit("refresh",to=request.sid)
        session["server"]=newServer
        join_room(newServer)
        if session.get("name") not in room_dict[newServer]["/"]:
            room_dict[newServer]["/"].append(session.get("name"))
            socketio.emit("serverlive",room_dict[newServer]["/"],room=newServer)
        # for i in channels:
        #     channel_list.append([i.name,i.user.username])
        channel_list=[session.get("server")]
        channel_list.append([[channel.name,channel.user.username] for channel in channels])
        channel_list.append([])
        socketio.emit("showNewServer",channel_list,to=request.sid)    
    else:
        session.clear()
        socketio.emit("Logout",to=request.sid)




@socketio.on("search_text")
def search(text):
    curr=session.get("server")
    channel_list=server[curr].query(channel).filter(channel.name.like("%"+text+"%")).all()
    user_list=server[curr].query(users).filter(users.username.like("%"+text+"%")).all()
    # result=[curr]
    # for item in channel_list:
    #     result.append([item.name,item.user.username])
    # for item in user_list:
    #     result.append([item.username,None])
    channels=[curr]
    channels.append([[channel.name,channel.user.username] for channel in channel_list])
    channels.append([[user.username] for user in user_list])
    socketio.emit("showNewServer",channels,to=request.sid)

@socketio.on('join_channel')
def handle_join_channel(curChannel):
    curr=session.get("server")
    name=session.get("name")
    # print("before joining")
    # print(socketio.server.manager.rooms)
    join_room(curr+curChannel)
    # print("after joining")
    # print(socketio.server.manager.rooms)
    # print("Request id : "+str(request.sid))
    # print("================================================")
    if curChannel in room_dict[curr]:
        if name not in room_dict[curr][curChannel]:
            room_dict[curr][curChannel].append(name)
    else:
        room_dict[curr][curChannel] = [name]
    socketio.emit('notify',room_dict[curr][curChannel],room= curr+curChannel)

@socketio.on("changeChannel")
def changeChannel(newChannel):
    curr=session.get("server")
    id = session.get(curr+'id')
    prevChannel = session.get('channel')
    if not prevChannel:
        prevChannel=session.get("key")
    if prevChannel:
        handle_leave_channel(prevChannel)
    current_channel=server[curr].query(channel).filter_by(name=newChannel).first()
    session["channel"]=current_channel.name
    handle_join_channel(current_channel.name)
    last_posts=server[curr].query(posts).order_by(posts.id.desc()).filter_by(channel_id=current_channel.id).limit(30)
    Posts=[None]
    for i in last_posts:
        Posts.append([i.user.username,i.data,i.time.strftime("%D  %H:%M")])
    if len(Posts)>1:
        Posts.pop(0)
        messageID=last_posts[-1].id
        Posts.append(messageID)
    socketio.emit('showHistory',Posts[::-1],to=request.sid)

@socketio.on('leave_channel')
def handle_leave_channel(prevChannel):
    curr=session.get("server")
    name=session.get("name")
    if not prevChannel:
        prevChannel=session.get("channel")
    if not prevChannel:
        prevChannel=session.get("key")
    # print("before leaving")
    # print(socketio.server.manager.rooms)
    leave_room(curr+prevChannel)
    # print("after leaving")
    # print(socketio.server.manager.rooms)
    # print("Request id : "+str(request.sid))
    # print("================================================")
    session["channel"]=None
    session["key"]=None
    if prevChannel in room_dict[curr]:
        if name in room_dict[curr][prevChannel]:
            room_dict[curr][prevChannel].remove(name)
            leave_room(curr+prevChannel)
    else:
        room_dict[curr][prevChannel]=[]
    socketio.emit('notify',room_dict[curr][prevChannel],room= curr+prevChannel)    

@socketio.on('recieve_message')
def handel_recieve_message(data):
    curr=session.get("server")
    name=session.get("name")
    id=session.get(curr)
    channel_name=session.get("channel")
    key=session.get("key")
    if channel_name:
        current_channel=server[curr].query(channel).filter_by(name=channel_name).first()
        msg=posts(data=data,sender_id=id,channel_id=current_channel.id)
        server[curr].add(msg)
        server[curr].commit()
        socketio.emit('show_message',[name,data,msg.time.strftime("%D  %H:%M")], room = curr+channel_name)
    else:
        msg=chats(data=data,key=key,sender_id=id)
        server[curr].add(msg)
        server[curr].commit()
        socketio.emit('show_message',[name,data,msg.time.strftime("%D  %H:%M")], room = curr+key)


# @socketio.on('recieve_private_message')
# def handel_recieve_private_message(data):
#     curr=session.get("server")
#     id = session.get(curr+"id")
#     prvt_key=session.get("key")
#     socketio.emit('show_private_message',[data,chat.data,chat.time.strftime("%D  %H:%M")], room=key)

    # socketio.emit('show_message',[data["user"],data["text"]], room =data['channel'])
# @socketio.on("changeFrnd")
# def handel_change_Frnd(Frnd):
#     curr=session.get("server")
#     id=session.get(curr+"id")
#     frnd_id

@socketio.on('enter_private')
def handle_enter_private(data):
    curr=session.get("server")
    if session.get("channel"):
        handle_leave_channel(session.get("channel"))
    id=session.get(curr)
    name=session.get("name")
    frnd=server[curr].query(users).filter_by(username=data).first()
    key=private_key(id,frnd.id)
    session["key"]=key
    join_room(curr+key)
    if key in room_dict[curr]:
        if name not in room_dict[curr][key]:
            room_dict[curr][key].append(name)
    else:
        room_dict[curr][key] = [name]
    history=server[curr].query(chats).order_by(chats.id.desc()).filter_by(key=key).limit(30)
    History=[None]
    for i in history:
        History.append([i.user.username,i.data,i.time.strftime("%D  %H:%M")])
    if len(History)>1:
        History.pop(0)
        messageID=history[-1].id
        History.append(messageID)
    socketio.emit("showHistory",History[::-1],to=request.sid)
    socketio.emit('notify',room_dict[curr][key],room= curr+key)


@socketio.on('getHistory')
def getHistory(last):
    curr=session.get("server")
    id=session.get('id')
    channel_name=session.get("channel")
    History=[None]
    if channel_name:
        current_channel=server[curr].query(channel).filter_by(name=channel_name).first()
        history=server[curr].query(posts).order_by(posts.id.desc()).filter(and_(posts.channel_id==current_channel.id,posts.id<last)).limit(30)
    else:
        history=server[curr].query(chats).order_by(chats.id.desc()).filter(and_(chats.id<last,chats.key==session.get("key"))).limit(30)
    for i in history:
        History.append([i.user.username,i.data,i.time.strftime("%D  %H:%M")])
    if len(History)>1:
        History.pop(0)
        messageID=history[-1].id
        History.append(messageID)
    socketio.emit('showHistory',History[::-1],to=request.sid)
    

# @app.route('/logout',methods=["POST"])
# def logout():
#     srvr=session.get("server")
#     name=session.get("name")
#     if name in room_dict[srvr]["/"]:
#         room_dict[srvr]["/"].remove(name)
#         emit("serverlive",room_dict[srvr]["/"],room=srvr)
#     print(room_dict[srvr]["/"])
#     session["name"]=None
#     session.clear()
#     print(session.get("name"))
#     print(session.get("server"))
#     print("done")
#     return redirect("/servers")
    


@app.route('/',methods=["GET","POST"])
def index():
    if session.get("name")==None:
        return redirect("/servers")
    else:
        return redirect("/channels")

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
            if len(serverList)==len(server):
                return redirect("/channels")
            done=loginlogic(name, password)
            if done:
                return redirect("/channels")
            else:
                return render_template("message.html",msg="YOUR OLD PASSWORD IS UPDATED WITH NEWONE",goto="/channels")



# @app.route('/delete' ,methods=["GET"])
# def delete_channel():
#     try:
#         data=channel.query.filter_by(id=session.get("channel")).first()
#         post=data.posts
#         for i in post:
#             db.session.delete(i)
#             db.session.commit()
#         db.session.delete(data)
#         db.session.commit()
#         session["channel"]=None
#     except:
#         return render_template("message.html",msg="no channel exist/can't delete")
#     funposts=short_posts.query.filter_by(sender_id=session.get("id")).all()
#     for i in funposts:
#         db.session.delete(i)
#         db.session.commit()
#     return redirect('/')

# @app.route('/delete_short' ,methods=["GET"])
# def delete_short():
#     user=int(session.get("id"))
#     if session.get("channel"):
#         try:
#             funposts=short_posts.query.filter_by(topic_id=session.get("channel"), sender_id=user).all()
#             for i in funposts:
#                 db.session.delete(i)
#                 db.session.commit()
#         except: 
#             return render_template("message.html",msg="can't delete for this channel")
#         session["body"]=""
#         session["fun"]="False"        
#         return redirect('/channels/')

#     elif session.get("frnd"):
#         try:
#             frnd=users.query.filter_by(id=session.get("frnd")).first()
#             prvt_key=private_key(user,frnd.id)
#             funposts=short_messages.query.filter_by(key=prvt_key).all()
#             for i in funposts:
#                 db.session.delete(i)
#                 db.session.commit()     
#             session["body"]=""
#             session["fun"]="False"
#             return redirect('/chat/'+str(frnd.id))
#         except:
#             return render_template("message.html",msg="can't delete for this chat")
#     else:        
#         return redirect('/')

# @app.route('/delete_chat' ,methods=["GET"])
# def delete_chat():
#     id=session.get("id")
#     Frnd=session.get("frnd")
#     friend=users.query.filter_by(id=Frnd).first()
#     frnd_id=friend.id
#     prvt_key=private_key(id,frnd_id)
#     try:
#         chat=chats.query.filter_by(key=prvt_key).all()
#         for i in chat:
#             db.session.delete(i)
#             db.session.commit()
#         session["frnd"]=None
#     except:
#         return render_template("message.html",msg="no channel exist/can't delete")
#     funposts=short_messages.query.filter_by(key=prvt_key).all()
#     for i in funposts:
#         db.session.delete(i)
#         db.session.commit()    
#     return redirect('/app')

@app.route("/app",methods=["POST","GET"])
def application():
    curr=session.get("server")
    id=session.get(curr)
    newChannel=request.form.get("channel_name")
    newChannel=str(newChannel).strip()
    try:
        topic=channel(name=newChannel,creator_id=id)
        server[curr].add(topic)
        server[curr].commit()
        room_dict[curr][newChannel]=[]
    except:
        return render_template("message.html",msg="can't add channel",goto="/channels")
    channels=server[curr].query(channel).all() # soon to emit to all people in server
    return render_template("searchresult.html",name=user,tables=channels,server=curr)

@app.route("/channels",methods=["GET"])
def channel_chat():
    if not session.get("name"):
        return redirect("/servers")
    curr=session.get("server")
    name=session.get("name")
    myserver=session.get("myserver")
    if myserver!=None:
        return render_template("channel_chat.html",name=name,server=curr,mysrvr=myserver)
    session.clear()
    return redirect("/login")    
                

# @app.route("/chat/<int:frnd>/<action>=<int:chat>",methods=["GET","POST"])
# def chat_history(frnd,action,chat):
#     if session.get("id")==None:
#         return redirect("/login")
#     id=session.get("id")
#     me=users.query.filter_by(id=id).first()
#     friend=users.query.filter_by(id=frnd).first()
#     session["frnd"]=friend.id
#     session["channel"]=None
#     prvt_key=private_key(me.id,friend.id)
#     if action=="next":
#         our_chats=chats.query.order_by(chats.id.asc()).filter(and_(chats.id>=chat,chats.key==prvt_key)).limit(7)
#         if our_chats.count()<7:
#             return redirect("/chat/"+str(frnd))
#     elif action=="prev":
#         last_chats=chats.query.order_by(chats.id.desc()).filter(and_(chats.id<=chat,chats.key==prvt_key)).limit(7)
#         if last_chats.count()<7:
#             our_chats=chats.query.filter_by(key=prvt_key).limit(7)
#         else:
#             our_chats = last_chats[::-1]
#     else:
#         return redirect("/chat/"+str(frnd))           
#     shortchat=[]
#     fun=session.get("fun")
#     body=session.get("body")
#     return render_template("chat.html",name=me,chats=our_chats,frnd=friend,feelings=shortchat,hide=session.get("fun"),body=session.get("body"))


#private key
def private_key(a,b):
    a=int(a)
    b=int(b)
    if a<=b:
        key=str(a)+"-"+str(b)
    else:
        key=str(b)+"-"+str(a)
    return hashlib.md5(key.encode()).hexdigest()


# @app.route("/chat/<frnd>",methods=["GET","POST"])
# def chat(frnd):
#     if session.get("id")==None:
#         return redirect("/login")
#     id=session.get("id")
#     fun=request.form.get("hide")
#     message=request.form.get("message")
#     me=users.query.filter_by(id=id).first()
#     friend=users.query.filter_by(username=frnd).first()
#     session["frnd"]=friend.id
#     session["channel"]=None


#private key
    # prvt_key=private_key(me.id,friend.id)
    # if message!=None:
    #     if fun=="True":
    #         try:
    #             chat=short_messages(data=message,key=prvt_key,sender_id=me.id)
    #             db.session.add(chat)
    #             db.session.commit()
    #             session["body"]="darkbody"
    #             session["fun"]="True"
    #             print("your uselessly chat is saved")
    #         except:
    #             return render_template("message.html",msg="can't post in short chats")
    #     else:
    #         try:
    #             chat=chats(data=message,key=prvt_key,sender_id=me.id)
    #             db.session.add(chat)
    #             db.session.commit()
    #         except:
    #             return render_template("message.html",msg="can't post in chats")
    #         session["body"]=""
    #         session["fun"]="False"
    #         funposts=short_messages.query.filter_by(key=prvt_key, sender_id=me.id).all()
    #         for i in funposts:
    #             db.session.delete(i)
    #             db.session.commit()
    # try:
    #     our_chats=chats.query.order_by(chats.id.desc()).filter_by(key=prvt_key).limit(15)
    #     our_chats=our_chats[::-1]
    #     shortchat=short_messages.query.filter_by(key=prvt_key).all()
    # except:
    #     return render_template("message.html",msg="plz give valid input or check code")    
    # return render_template("chat.html",name=me,chats=our_chats,frnd=friend,feelings=shortchat,hide=session.get("fun"),body=session.get("body"))


@app.route('/download/<server>')
def download_database(server):
    if server=="app":
        path= str(app.config['SQLALCHEMY_DATABASE_URI']).rsplit("///")[1]
    else:
        path =str(app.config['SQLALCHEMY_BINDS'][str(server)]).rsplit("///")[1]
    return send_file(path, as_attachment=True)



# @app.route('/test',methods=['GET'])
# def test():
#     testA="$5$rounds=535000$geol8OJlueagKggX$yfCV4SDlZJTzjCy4gOhUBqmO5uOArL.QzHjx6NXY4L1"
#     testB="$5$rounds=535000$UJ4XGia5irCQ6V1f$JK4MLGqMgFnsb8OxYqebFgxCCafLHpWhJHC9mpFwCAA"
#     if sha256_crypt.verify("montirathee",testA):
#         print("testA")
#     else:
#         print("Not testA")
#     if sha256_crypt.verify("montirathee",testB):
#         print("testB")
#     else:
#         print("Not testB")
#     return render_template("message.html",msg="test",goto="/test")


#     # file=request.files['file']
    # if file and file.filename!="db.sqlite3" and file.filename.rsplit(".")[1]=="sqlite3":
    #     uploads_dir = os.path.join('db')
    #     if os.path.exists(uploads_dir)==False:
    #         print("true")
    #         os.makedirs(uploads_dir)
    #     file.save(os.path.join(uploads_dir,secure_filename(file.filename)))
    # #     return redirect("/")
    # # return redirect("/")
    # print(os.listdir("db"))
    # databases=[]
    # for db in os.listdir("db"):
    #     databases.append(db)
    #     print(databases)
    # return render_template("database.html",databases=data)

if __name__ == '__main__':
    socketio.run(app)




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
app.config['SECRET_KEY'] ="secret!"  #os.environ.get('SECRET_KEY')
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
    chat=db.relationship('chats',backref='sender')
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

room_dict={"app":{}}
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
    file=request.files['file']
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
        room_dict[data]={}
        session["server"]=None
        return redirect("/servers")
    else:
        return render_template("message.html",msg="select a valid database file or rename it except db.sqlite3.")

@app.route('/servers',methods=["POST","GET"])
def change_db():
    if os.path.exists("db")==False:
        os.makedirs("db")
    databases=[]
    for db in os.listdir("db"):
        databases.append(db.split(".")[0]) 
    if request.method=="GET":
        try:
            if session["server"]!=None:
                return redirect("/login")
            else:
                return render_template("database.html",databases=databases)
        except:
            session["server"]=None
    try:
        data=request.form['server']
    except:
        data=False
    # if not data:
    #     return render_template("database.html",databases=databases)
    if data:
        session["server"]=data
        session["id"]=None
        session["channel"]=None
        return redirect("/login")
    else:
        session["server"]=None
        return render_template("database.html",databases=databases)
    # try:
    #     deldb=request.form['deldb']
    # except:
    #     deldb=False
    # if deldb:
    #     os.remove("db/"+str(deldb).rsplit("-")[1])
    #     app.config['SQLALCHEMY_DATABASE_URI'] ="sqlite:///db.sqlite3"
    #     return redirect("/servers")



@app.route('/',methods=["GET","POST"])
def index():
    if session.get("server")==None:
        return redirect("/servers")
    if session.get("id")==None:
        return redirect("/login")
    # if session.get("channel")!=None:
    #     return redirect("/channels")
    elif session.get("chat")!=None:
        return redirect("/chat/"+str(session.get("frnd")))
    else:
        return redirect("/app")

# @socketio.on('join_server')
# def handel_join_server():
#     join_room(session.get("server"))
#     print("Joined server name: "+session.get("server"))

@socketio.on("changeServer")
def changeServer(newServer):
    oldServer=session.get("server")
    if oldServer:
        leave_room(oldServer)
    session["server"]=newServer
    join_room(newServer)
    curr=newServer
    channels=server[curr].query(channel).all()
    channel_list=[]
    for i in channels:
        channel_list.append([i.name,i.user.username])
    socketio.emit("showNewServer",channel_list,to=request.sid)    

@socketio.on('join_channel')
def handle_join_channel(curChannel):
    curr=session.get("server")
    id = session.get(curr+"id")
    user=server[curr].query(users).filter_by(id=id).first()
    # print("before joining")
    # print(socketio.server.manager.rooms)
    join_room(curr+curChannel)
    # print("after joining")
    # print(socketio.server.manager.rooms)
    # print("Request id : "+str(request.sid))
    # print("================================================")
    if curChannel in room_dict[curr]:
        if user.username not in room_dict[curr][curChannel]:
            room_dict[curr][curChannel].append(user.username)
    else:
        room_dict[curr][curChannel] = [user.username]
    socketio.emit('notify',room_dict[curr][curChannel],room= curr+curChannel)

@socketio.on('leave_channel')
def handle_leave_channel(prevChannel):
    curr=session.get("server")
    id = session.get(curr+"id")
    # print("before leaving")
    # print(socketio.server.manager.rooms)
    leave_room(curr+prevChannel)
    # print("after leaving")
    # print(socketio.server.manager.rooms)
    # print("Request id : "+str(request.sid))
    # print("================================================")
    session[curr+"channel"]=None
    user=server[curr].query(users).filter_by(id=id).first()
    if prevChannel in room_dict[curr]:
        if user.username in room_dict[curr][prevChannel]:
            room_dict[curr][prevChannel].remove(user.username)
            leave_room(curr+prevChannel)
    else:
        room_dict[curr][prevChannel]=[]
    socketio.emit('notify',room_dict[curr][prevChannel],room= curr+prevChannel)    

@socketio.on('recieve_message')
def handel_recieve_message(data):
    curr=session.get("server")
    id=session.get(curr+"id")
    channel_name=session.get(curr+"channel")
    user = server[curr].query(users).filter_by(id=id).first()
    current_channel=server[curr].query(channel).filter_by(name=channel_name).first()
    post=posts(data=data,sender_id=user.id,channel_id=current_channel.id)
    server[curr].add(post)
    server[curr].commit()
    socketio.emit('show_message',[post.user.username,post.data,post.time.strftime("%D  %H:%M")], room = curr+channel_name)


    # socketio.emit('show_message',[data["user"],data["text"]], room =data['channel'])

@socketio.on('enter_private')
def handle_enter_private(data):
    key=private_key_string(data['myId'], data['frndId'])
    join_room(key)
    socketio.emit('notify',data['name'],room=key)

@socketio.on('recieve_private_message')
def handel_recieve_private_message(data):
    curr=session.get("server")
    id = session.get(curr+"id")
    frndId = session.get("frnd")
    key = private_key_string(id, frndId)
    prvt_key = private_key(id, frndId)
    try:
        chat=chats(data=data['text'],key=prvt_key,sender_id=id)
        db.session.add(chat)
        db.session.commit()
    except:
        return render_template("message.html",msg="can't post in chats")
    last_chat=chats.query.order_by(chats.id.desc()).filter(chats.key==prvt_key).limit(1)
    lastchat=last_chat[0]
    socketio.emit('show_private_message',[data["name"],lastchat.data,lastchat.time.strftime("%D  %H:%M")], room=key)

@socketio.on('getHistory')
def getHistory(post):
    curr=session.get("server")
    id=session.get('id')
    channel_name=session.get(curr+"channel")
    current_channel=server[curr].query(channel).filter_by(name=channel_name).first()
    history=server[curr].query(posts).order_by(posts.id.desc()).filter(and_(posts.channel_id==current_channel.id,posts.id<post)).limit(30)
    History=[None]
    for i in history:
        History.append([i.user.username,i.data,i.time.strftime("%D  %H:%M")])
    if len(History)>1:
        History.pop(0)
        messageID=history[-1].id
        History.append(messageID)
    socketio.emit('showHistory',History[::-1],to=request.sid)
    
    
@socketio.on("changeChannel")
def changeChannel(newChannel):
    curr=session.get("server")
    id = session.get(curr+'id')
    prevChannel = session.get(curr+'channel')
    if prevChannel:
        handle_leave_channel(prevChannel)
    current_channel=server[curr].query(channel).filter_by(name=newChannel).first()
    session[curr+"channel"]=current_channel.name
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



@app.route('/login',methods=["GET","POST"])
def login():
    if request.method=="GET":
        if session.get("login")==None:
            allServers=[]
            for srvr in server.keys():
                if srvr!="app":
                    allServers.append(srvr)
            return render_template("login.html",servers=allServers)
        else:
            return redirect("/channels")
    else:
        name=str(request.form.get("username")).lower()
        password=str(request.form.get("password")).lower()
        operation=request.form.get("operation")
        if operation == "login":
            myServer=[]
            for srvr in server.keys():
                user = server[srvr].query(users).filter_by(username=name).first()
                if user!=None:
                    if sha256_crypt.verify(str(name+password), user.password):
                        session["login"]=True
                        myServer.append(srvr)
                        session[srvr+"id"]=user.id
                        if session["server"]==None:
                            session["server"]=srvr
            session["myserver"]=myServer[:]
            return redirect("/channels")
            # return render_template("searchresult.html",name=realuser,tables=tables,mysrvr=myServer,server=srvr)
                #        return  redirect("/")
                #     else:    
                #         return render_template("message.html",msg="incorrect password")
                # else:        
                #     return render_template("message.html",msg="Username doesn't exist")

        if operation == "register":
            serverList=request.form.getlist("server[]")
            if len(serverList)==0:
                return render_template("message.html",msg="Select atleast one server")
            for srvr in serverList:
                user=server[srvr].query(users).filter_by(username=name).first()
                if user!=None:
                    return render_template("message.html",msg="Username exist")
            for srvr in serverList:
                user=users(username=name,password=sha256_crypt.encrypt(name+password),balance=0)
                server[srvr].add(user)
                server[srvr].commit()
                session["login"]=True
                session[srvr+"id"] =user.id
                if session.get("server")==None:
                    session["server"]=srvr
            session["myserver"]=serverList[:]
            return  redirect("/")

            
@app.route('/logout',methods=["GET","POST"])  
def logout():
    session["login"]=None
    session["myserver"]=None
    session["server"]=None
    session["id"]=None
    session["channel"]=None
    return redirect("/servers")


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

# @app.route('/reset',methods=["POST"])    
# def reset():
#     try:
#         post= posts.query.all()
#         for i in post:
#             db.session.delete(i)
#             db.session.commit()
#         user = users.query.all()
#         for i in user:
#             db.session.delete(i)
#             db.session.commit()
#         data = channel.query.all()
#         for i in data:
#             db.session.delete(i)
#             db.session.commit()
#         chat=chats.query.all()
#         for i in data:
#             db.session.delete(i)
#             db.session.commit()
#         session["id"]=None
#         session["channel"]=None
#         return redirect("/login")
#     except:
#         return render_template("message.html",msg="can't delete plz check your data")


@app.route("/app",methods=["POST"])
def application():
    curr=session.get("server")
    id=session.get(curr+"id")
    user=server[curr].query(users).filter_by(id=id).first()
    # if session.get(curr+"channel") in room_dict[curr]:
    #     if user.username in  room_dict[curr][session.get(curr+"channel")]:
    #         room_dict[curr][session.get('channel')].remove(user.username)
    #         handle_leave_channel(False)
    # session["channel"]=None 
    # session["frnd"]=None
    # session["body"]=None
    # session["fun"]=None
    newChannel=request.form.get("channel_name")
    searchRequest=request.form.get("search")

    if searchRequest!=None:
        results=[]
        searching_for=searchRequest.strip()
        channel_list=server[curr].query(channel).filter(channel.name.like("%"+searching_for+"%")).all()
        user_list=server[curr].query(users).filter(users.username.like("%"+searching_for+"%")).all()
        results.extend(channel_list)
        results.extend(user_list)
        return render_template("searchresult.html",name=user,tables=results)
    
    elif newChannel!=None:
        str(newChannel).strip()
        try:
            topic=channel(name=newChannel,creator_id=user.id)
            server[curr].add(topic)
            server[curr].commit()
            room_dict[curr][newChannel]=[]
        except:
            return render_template("message.html",msg="can't add channel")
    channels=server[curr].query(channel).all()
    # return render_template("user.html",name=user.username,balance=user.balance,tables=channels)
    # if server:
    #     print(DataBases)
    #     print(DataBases[str(s)+"users"])
    #     print(users)
    #     user=server[str(s)+"session"].query(users).filter_by(id=id).first()
    #     channels=server[str(s)+"session"].query(channel).all()
    return render_template("searchresult.html",name=user,tables=channels,server=curr)

@app.route("/channels",methods=["GET","POST"])
def channel_chat():
    if session.get("login")!=True:
        return redirect("/login")
    curr=session.get("server")
    id=session.get(curr+"id")
    user = server[curr].query(users).filter_by(id=id).first()
    tables=server[curr].query(channel).all()
    return render_template("channel_chat.html",name=user,tables=tables,server=curr,mysrvr=session.get("myserver"))
        
                

@app.route("/chat/<int:frnd>/<action>=<int:chat>",methods=["GET","POST"])
def chat_history(frnd,action,chat):
    if session.get("id")==None:
        return redirect("/login")
    id=session.get("id")
    me=users.query.filter_by(id=id).first()
    friend=users.query.filter_by(id=frnd).first()
    session["frnd"]=friend.id
    session["channel"]=None
    prvt_key=private_key(me.id,friend.id)
    if action=="next":
        our_chats=chats.query.order_by(chats.id.asc()).filter(and_(chats.id>=chat,chats.key==prvt_key)).limit(7)
        if our_chats.count()<7:
            return redirect("/chat/"+str(frnd))
    elif action=="prev":
        last_chats=chats.query.order_by(chats.id.desc()).filter(and_(chats.id<=chat,chats.key==prvt_key)).limit(7)
        if last_chats.count()<7:
            our_chats=chats.query.filter_by(key=prvt_key).limit(7)
        else:
            our_chats = last_chats[::-1]
    else:
        return redirect("/chat/"+str(frnd))           
    shortchat=[]
    fun=session.get("fun")
    body=session.get("body")
    return render_template("chat.html",name=me,chats=our_chats,frnd=friend,feelings=shortchat,hide=session.get("fun"),body=session.get("body"))

# for key string
def private_key_string(a,b):
    a=int(a)
    b=int(b)
    if a<b:
        key=str(a)+"-"+str(b)
    elif b<a:
        key=str(b)+"-"+str(a)
    else:
        key=str(a)+"-"+str(b)
    return key
#private key
def private_key(a,b):
    key=private_key_string(a, b)
    return hashlib.md5(key.encode()).hexdigest()


@app.route("/chat/<frnd>",methods=["GET","POST"])
def chat(frnd):
    if session.get("id")==None:
        return redirect("/login")
    id=session.get("id")
    fun=request.form.get("hide")
    message=request.form.get("message")
    me=users.query.filter_by(id=id).first()
    friend=users.query.filter_by(username=frnd).first()
    session["frnd"]=friend.id
    session["channel"]=None


#private key
    prvt_key=private_key(me.id,friend.id)
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
    try:
        our_chats=chats.query.order_by(chats.id.desc()).filter_by(key=prvt_key).limit(15)
        our_chats=our_chats[::-1]
        shortchat=short_messages.query.filter_by(key=prvt_key).all()
    except:
        return render_template("message.html",msg="plz give valid input or check code")    
    return render_template("chat.html",name=me,chats=our_chats,frnd=friend,feelings=shortchat,hide=session.get("fun"),body=session.get("body"))


@app.route('/download/<server>')
def download_database(server):
    if server=="app":
        path= str(app.config['SQLALCHEMY_DATABASE_URI']).rsplit("///")[1]
    else:
        path =str(app.config['SQLALCHEMY_BINDS'][str(server)]).rsplit("///")[1]
    return send_file(path, as_attachment=True)



# @app.route('/test',methods=['GET'])
# def test():
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

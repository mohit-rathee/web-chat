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

channel_post=db.Table('channel_post',
    db.Column('channel',db.Integer,db.ForeignKey('channel.id')),
    db.Column('posts',db.Integer,db.ForeignKey('posts.id')))

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
    topic=db.relationship('channel',secondary=channel_post,backref=db.backref('posts',lazy='dynamic'))      #Association table->channel_post

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

room_dict={}


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
    if file and file.filename.rsplit(".")[1]=="sqlite3":
        uploads_dir = os.path.join('db')
        if os.path.exists(uploads_dir)==False:
            os.makedirs(uploads_dir)
        file.save(os.path.join(uploads_dir,secure_filename(file.filename)))
        try:
            app.config['SQLALCHEMY_DATABASE_URI'] ="sqlite:///"+str(os.path.join(uploads_dir,secure_filename(file.filename)))
        except:
            file.remove(os.path.join(uploads_dir,secure_filename(file.filename)))
            return render_template("message.html",msg="Coudn't set to this database.")
        return redirect("/session")
    else:
        return render_template("message.html",msg="select a valid database file or rename it except db.sqlite3.")

@app.route('/session',methods=["POST","GET"])
def change_db():
    if os.path.exists("db")==False:
        os.makedirs("db")
    databases=[]
    for db in os.listdir("db"):
        databases.append(db) 
    if request.method=="GET":
        return render_template("database.html",databases=databases)
    if request.method=="POST":
        try:
            data=request.form['database']
        except:
            data=False
        try:
            deldb=request.form['deldb']
        except:
            deldb=False
            
        if data:
            app.config['SQLALCHEMY_DATABASE_URI'] ="sqlite:///db/"+str(data)
            return render_template("login.html",dbsession=data)
        elif deldb:
            os.remove("db/"+str(deldb).rsplit("-")[1])
            app.config['SQLALCHEMY_DATABASE_URI'] ="sqlite:///db.sqlite3"
            return redirect("/session")
        

@app.route('/',methods=["GET","POST"])
def index():
    if session.get("id")==None:
        return redirect("/login")
    if session.get("channel")!=None:
        return redirect("/channels")
    elif session.get("chat")!=None:
        return redirect("/chat/"+str(session.get("frnd")))
    else:
        return redirect("/app")

@socketio.on('join_channel')
def handle_join_channel():
    id = session.get("id")
    curChannel=session.get("channel")
    print(str(id)+" joined the "+str(curChannel))
    user=users.query.filter_by(id=id).first()
    join_room(curChannel)
    if curChannel in room_dict:
        if user.username not in room_dict[curChannel]:
            room_dict[curChannel].append(user.username)
    else:
        room_dict[curChannel] = [user.username]
    print(room_dict)
    socketio.emit('notify',room_dict[curChannel],room= curChannel)

@socketio.on('leave_channel')
def handle_leave_channel(data=True):
    prevChannel=session.get("channel")
    if data:
        id = session.get("id")
        leave_room(prevChannel)
        session["channel"]=0
        user=users.query.filter_by(id=id).first()
        if prevChannel in room_dict:
            if user.username in room_dict[prevChannel]:
                room_dict[prevChannel].remove(user.username)
                leave_room(prevChannel)
        else:
            room_dict[prevChannel]=[]
    else:
        if prevChannel not in room_dict:
            room_dict[prevChannel]=[]
    socketio.emit('notify',room_dict[prevChannel],room= prevChannel)    

@socketio.on('recieve_message')
def handel_recieve_message(data):
    id=session.get("id")
    channel_name=session.get("channel")
    user = users.query.filter_by(id=id).first()
    current_channel=channel.query.filter_by(name=channel_name).first()
    post=posts(data=data,sender_id=user.id)
    post.topic.append(current_channel)
    db.session.add(post)
    db.session.commit()
    last_posts=current_channel.posts.order_by(posts.id.desc()).limit(1)
    lastpost=last_posts[0]
    socketio.emit('show_message',[lastpost.user.username,lastpost.data,lastpost.time.strftime("%D  %H:%M")], room = channel_name)


    # socketio.emit('show_message',[data["user"],data["text"]], room =data['channel'])

@socketio.on('enter_private')
def handle_enter_private(data):
    key=private_key_string(data['myId'], data['frndId'])
    join_room(key)
    socketio.emit('notify',data['name'],room=key)

@socketio.on('recieve_private_message')
def handel_recieve_private_message(data):
    id = session.get("id")
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
    id=session.get('id')
    channel_name=session.get("channel")
    # print("show history for: "+str(id))
    current_channel=channel.query.filter_by(name=channel_name).first()
    history=current_channel.posts.order_by(posts.id.desc()).filter(posts.id<post).limit(30)
    History=[None]
    for i in history:
        History.append([i.user.username,i.data,i.time.strftime("%D  %H:%M")])
    if len(History)>1:
        History.pop(0)
        messageID=history[-1].id
        History.append(messageID)
    print(request.sid)
    socketio.emit('showHistory',History[::-1],to=request.sid)
    
    
@socketio.on("changeChannel")
def changeChannel(newChannel):
    id = session.get('id')
    prevChannel = session.get('channel')
    handle_leave_channel()
    current_channel=channel.query.filter_by(name=newChannel).first()
    session["channel"]=current_channel.name
    handle_join_channel()
    last_posts=current_channel.posts.order_by(posts.id.desc()).limit(30)
    Posts=[None]
    for i in last_posts:
        Posts.append([i.user.username,i.data,i.time.strftime("%D  %H:%M")])
    if len(Posts)>1:
        Posts.pop(0)
        messageID=last_posts[-1].id
        Posts.append(messageID)
    print(request.sid)
    socketio.emit('showHistory',Posts[::-1],to=request.sid)



@app.route('/login',methods=["GET","POST"])
def login():
    if request.method=="GET":
        return render_template("login.html")
    if request.method=="POST":
        name=str(request.form.get("username")).lower()
        password=str(request.form.get("password")).lower()
        operation=request.form.get("operation")
        coupon=request.form.get("coupon")
        power=request.form.get("power")
        send=request.form.get("send")
        if operation == "login":
            try:
                user = users.query.filter_by(username=name).first()
                if sha256_crypt.verify(str(name+password), user.password):
                    session["id"]=user.id
                    return  redirect("/")
                else:    
                    return render_template("message.html",msg="incorrect password")
            except:
                return render_template("message.html",msg="Username doesn't exist")

        if operation == "register":
            user = users.query.filter_by(username=name).first()
            if user!=None:
                return render_template("message.html",msg="Username exist")
            user=users(username=name,password=sha256_crypt.encrypt(name+password),balance=0)
            db.session.add(user)
            db.session.commit()
            user = users.query.filter_by(username=name).first()
            session["id"] =user.id
            return  redirect("/")
        if send=="register":
            return render_template("register.html")  
        elif send=="login":
            return redirect("/login")

            
@app.route('/logout',methods=["GET","POST"])  
def logout():
    user = users.query.filter_by(id=session.get('id')).first()
    if session.get('channel'):
        if user.username in room_dict[session.get('channel')]:
            room_dict[session.get('channel')].remove(user.username)
            handle_leave_channel(False)
    session["id"]=None
    session["channel"]=None
    return redirect("login")


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


@app.route("/app",methods=["GET","POST"])
def application():
    if session.get("id")==None:
        return redirect("/login")
    id=session.get("id")
    user=users.query.filter_by(id=id).first()
    if session.get("channel") in room_dict:
        if user.username in  room_dict[session.get("channel")]:
            room_dict[session.get('channel')].remove(user.username)
            handle_leave_channel(False)
    session["channel"]=None 
    session["frnd"]=None
    session["body"]=None
    session["fun"]=None
    newChannel=request.form.get("channel_name")
    searchRequest=request.form.get("search")
    if searchRequest!=None:
        results=[]
        searching_for=searchRequest.strip()
        try:
            channel_list=channel.query.filter(channel.name.like("%"+searching_for+"%")).all()
            results.extend(channel_list)
        except:
            print("error")
        try:
            user_list=users.query.filter(users.username.like("%"+searching_for+"%")).all()
            results.extend(user_list)
        except:
            print("error")
        return render_template("searchresult.html",name=user,tables=results)
    
    elif newChannel!=None:
        str(newChannel).strip()
        try:
            topic=channel(name=newChannel,creator_id=user.id)
            room_dict[newChannel]=[]
            db.session.add(topic)
            db.session.commit()
            print("sucess")
        except:
            return render_template("message.html",msg="can't add channel")
        try:
            channels=channel.query.all()
        except:
            print("can't show topics id")
        # return render_template("user.html",name=user.username,balance=user.balance,tables=channels)
        return render_template("searchresult.html",name=user,tables=channels)
    else:
        channels=channel.query.all()
        # return render_template("user.html",name=user.username,balance=user.balance,tables=channels)
        return render_template("searchresult.html",name=user,tables=channels)

@app.route("/channels",methods=["GET"])
def channel_chat():
    if session.get("id")==None:
        return redirect("/login")
    id=session.get("id")
    user = users.query.filter_by(id=id).first()
    channel_name = session.get('channel')
    if channel_name:
        current_channel=channel.query.filter_by(name=channel_name).first()
    else:
        current_channel=channel.query.filter_by(id=1).first()
    session["channel"]=current_channel.name
    tables=channel.query.all()
    last_posts=current_channel.posts.order_by(posts.id.desc()).limit(30)
    if last_posts.count()!=0:
        topic_posts=last_posts[::-1]
    else:
        topic_posts=[]
    shortPost=short_posts.query.filter_by(topic_id=channel_name).all()
    return render_template("channel_chat.html",name=user,posts=topic_posts,topic=current_channel,tables=tables,feelings=[],hide=session.get("fun"),body=session.get("body"),)
        

# @app.route("/<int:channel_id>/<action>=<int:post>",methods=["GET","POST"])
# def post_history(channel_id,action,post):
#     if session.get("id")==None:
#         return redirect("/login")
#     id=session.get("id")
#     user = users.query.filter_by(id=id).first()
#     current_channel=channel.query.filter_by(id=channel_id).first()
#     if action=="next":
#         topic_posts=current_channel.posts.order_by(posts.id.asc()).filter(posts.id>=post).limit(30)
#         if topic_posts.count()<7:
#             return redirect("/channels/"+str(channel_id))
#     elif action=="prev":
#         last_posts=current_channel.posts.order_by(posts.id.desc()).filter(posts.id<=post).limit(30)
#         if last_posts.count()<7:
#             topic_posts=current_channel.posts.limit(7)
#         else:
#             # new_post=last_posts[-1]
#             # newstart=new_post.id
#             # topic_posts=current_channel.posts.order_by(posts.id.asc()).filter(posts.id>=newstart).limit(7)
#             topic_posts = last_posts[::-1]


#     tables=channel.query.all()
#     current_channel=channel.query.filter_by(id=channel_id).first()
#     shortPost=[]
#     fun=session.get("fun")
#     body=session.get("body")
#     print("my work is done")
#     return render_template("channel_chat.html",name=user,posts=topic_posts,topic=current_channel,tables=tables,feelings=shortPost,hide=fun,body=body)
                

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


@app.route('/download')
def download_database():
    path= str(app.config['SQLALCHEMY_DATABASE_URI']).rsplit("///")[1]
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

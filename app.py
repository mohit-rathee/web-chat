from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
from datetime import timezone
from sqlalchemy.sql import func
from passlib.hash import sha256_crypt
import hashlib 
from flask_socketio import SocketIO, join_room, emit




app = Flask(__name__)
app.config.from_object(__name__)
socketio = SocketIO(app)
app.config['SECRET_KEY'] = 'secret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.sqlite3'
db = SQLAlchemy(app)

# engine = create_engine('sqlite:///test.sqlite3', echo=True)

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


# Routes
@app.before_request
def hello():
    print(request.path+"/"+request.method)


@app.teardown_request
def teardown_request(exception):
    print("done")

@app.route('/',methods=["GET","POST"])
def index():
    if session.get("id")==None:
        return redirect("/login")
    if session.get("channel")!=None:
        return redirect("/channel/"+str(session.get("channel")))
    elif session.get("chat")!=None:
        return redirect("/chat/"+str(session.get("frnd")))
    else:
        return redirect("/app")

@socketio.on('join_channel')
def handle_join_channel(data):
    join_room(data['channel'])


@socketio.on('order_refresh')
def handel_order_refresh(data):
    socketio.emit('refresh',data, room =data['channel'])



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
                print(user)
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
    session["id"]=None
    print(session["id"])
    return redirect("login")


@app.route('/delete' ,methods=["GET"])
def delete_channel():
    try:
        data=channel.query.filter_by(id=session.get("channel")).first()
        post=data.posts
        for i in post:
            db.session.delete(i)
            db.session.commit()
        db.session.delete(data)
        db.session.commit()
        session["channel"]=None
    except:
        return render_template("message.html",msg="no channel exist/can't delete")
    funposts=short_posts.query.filter_by(sender_id=session.get("id")).all()
    for i in funposts:
        db.session.delete(i)
        db.session.commit()
    return redirect('/')

@app.route('/delete_short' ,methods=["GET"])
def delete_short():
    user=int(session.get("id"))
    if session.get("channel"):
        try:
            funposts=short_posts.query.filter_by(topic_id=session.get("channel"), sender_id=user).all()
            for i in funposts:
                db.session.delete(i)
                db.session.commit()
        except: 
            return render_template("message.html",msg="can't delete for this channel")
        print("deleted")
        session["body"]=""
        session["fun"]="False"        
        return redirect('/channel/'+str(session.get("channel")))

    elif session.get("frnd"):
        try:
            frnd=users.query.filter_by(id=session.get("frnd")).first()
            prvt_key=private_key(user,frnd.id)
            funposts=short_messages.query.filter_by(key=prvt_key).all()
            for i in funposts:
                db.session.delete(i)
                db.session.commit()       
            print("deleted")
            session["body"]=""
            session["fun"]="False"
            return redirect('/chat/'+str(frnd.id))
        except:
            return render_template("message.html",msg="can't delete for this chat")
    else:        
        return redirect('/')

@app.route('/delete_chat' ,methods=["GET"])
def delete_chat():
    id=session.get("id")
    Frnd=session.get("frnd")
    friend=users.query.filter_by(id=Frnd).first()
    frnd_id=friend.id
    prvt_key=private_key(id,frnd_id)
    try:
        chat=chats.query.filter_by(key=prvt_key).all()
        for i in chat:
            db.session.delete(i)
            db.session.commit()
        session["frnd"]=None
    except:
        return render_template("message.html",msg="no channel exist/can't delete")
    funposts=short_messages.query.filter_by(key=prvt_key).all()
    for i in funposts:
        db.session.delete(i)
        db.session.commit()    
    return redirect('/app')

@app.route('/reset',methods=["POST"])    
def reset():
    try:
        post= posts.query.all()
        for i in post:
            db.session.delete(i)
            db.session.commit()
        user = users.query.all()
        for i in user:
            db.session.delete(i)
            db.session.commit()
        data = channel.query.all()
        for i in data:
            db.session.delete(i)
            db.session.commit()
        chat=chats.query.all()
        for i in data:
            db.session.delete(i)
            db.session.commit()
        print("delete")
        session["id"]=None
        session["channel"]=None
        return redirect("/login")
    except:
        return render_template("message.html",msg="can't delete plz check your data")


@app.route("/app",methods=["GET","POST"])
def application():
    if session.get("id")==None:
        return redirect("/login")
    session["channel"]=None 
    session["frnd"]=None
    session["body"]=None
    session["fun"]=None
    id=session.get("id")
    newChannel=request.form.get("channel_name")
    searchRequest=request.form.get("search")
    user=users.query.filter_by(id=id).first()
    if searchRequest!=None:
        results=[]
        searching_for=searchRequest.strip()
        print(searching_for)
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

@app.route("/channel/<int:channel_id>",methods=["GET","POST"])
def channel_chat(channel_id):
    if session.get("id")==None:
        return redirect("/login")
    id=session.get("id")
    session["fun"]=request.form.get("hide")
    post_data=request.form.get("post")
    user = users.query.filter_by(id=id).first()
    try:
        current_channel=channel.query.filter_by(id=channel_id).first()
        session["channel"]=current_channel.id
    except:
        return render_template("message.html",msg="channel not found")
    if session.get("channel"):
        if post_data!=None:
            if session.get("fun")=="True":
                #add short messages#
                msg=short_posts(data=post_data,sender_id=user.id,topic_id=channel_id)
                db.session.add(msg)
                db.session.commit()
                session["body"]="darkbody"
                session["fun"]="True"
                print("send an friendly message")
            else:
                post=posts(data=post_data,sender_id=user.id)
                post.topic.append(current_channel)
                db.session.add(post)
                db.session.commit()
                funposts=short_posts.query.filter(and_(short_posts.topic_id==session.get("channel"),short_posts.sender_id==user.id)).all()
                for i in funposts:
                    db.session.delete(i)
                    db.session.commit()
                session["body"]=""
                session["fun"]="False"
                print("posted")
                            
        tables=channel.query.all()
        current_channel=channel.query.filter_by(id=channel_id).first()

        
        last_posts=current_channel.posts.order_by(posts.id.desc()).limit(7)
        if last_posts.count()!=0:
            last_one=last_posts[-1]
            last_id=last_one.id
            print(last_id)
            topic_posts=current_channel.posts.order_by(posts.id.asc()).filter(posts.id>=last_id).limit(7)
        else:
            topic_posts=[]
        shortPost=short_posts.query.filter_by(topic_id=channel_id).all()
        print("my work is done")
        return render_template("channel_chat.html",name=user,posts=topic_posts,topic=current_channel,tables=tables,feelings=shortPost,hide=session.get("fun"),body=session.get("body"),)
                
    else:
        return render_template("message.html",msg="channel don't exist")

@app.route("/<int:channel_id>/<action>=<int:post>",methods=["GET","POST"])
def post_history(channel_id,action,post):
    if session.get("id")==None:
        return redirect("/login")
    id=session.get("id")
    user = users.query.filter_by(id=id).first()
    current_channel=channel.query.filter_by(id=channel_id).first()
    if action=="next":
        topic_posts=current_channel.posts.order_by(posts.id.asc()).filter(posts.id>=post).limit(7)
        if topic_posts.count()<7:
            return redirect("/channel/"+str(channel_id))
    elif action=="prev":
        last_posts=current_channel.posts.order_by(posts.id.desc()).filter(posts.id<=post).limit(7)
        if last_posts.count()<7:
            topic_posts=current_channel.posts.limit(7)
        else:
            # new_post=last_posts[-1]
            # newstart=new_post.id
            # topic_posts=current_channel.posts.order_by(posts.id.asc()).filter(posts.id>=newstart).limit(7)
            topic_posts = last_posts[::-1]


    tables=channel.query.all()
    current_channel=channel.query.filter_by(id=channel_id).first()
    shortPost=[]
    fun=session.get("fun")
    body=session.get("body")
    print("my work is done")
    return render_template("channel_chat.html",name=user,posts=topic_posts,topic=current_channel,tables=tables,feelings=shortPost,hide=fun,body=body)
                

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
    print("my work is done")
    return render_template("chat.html",name=me,chats=our_chats,frnd=friend,feelings=shortchat,hide=session.get("fun"),body=session.get("body"))


#private key
def private_key(a,b):
    if a<b:
        key=str(a)+"-"+str(b)
    elif b<a:
        key=str(b)+"-"+str(a)
    else:
        key=str(a)+"-"+str(b)
    return hashlib.md5(key.encode()).hexdigest()


@app.route("/chat/<int:frnd>",methods=["GET","POST"])
def chat(frnd):
    if session.get("id")==None:
        return redirect("/login")
    id=session.get("id")
    fun=request.form.get("hide")
    message=request.form.get("message")
    me=users.query.filter_by(id=id).first()
    friend=users.query.filter_by(id=frnd).first()
    session["frnd"]=friend.id
    session["channel"]=None


#private key
    prvt_key=private_key(me.id,friend.id)
    print(prvt_key)
    if message!=None:
        if fun=="True":
            try:
                chat=short_messages(data=message,key=prvt_key,sender_id=me.id)
                db.session.add(chat)
                db.session.commit()
                session["body"]="darkbody"
                session["fun"]="True"
                print("your uselessly chat is saved")
            except:
                return render_template("message.html",msg="can't post in short chats")
        else:
            try:
                chat=chats(data=message,key=prvt_key,sender_id=me.id)
                db.session.add(chat)
                db.session.commit()
            except:
                return render_template("message.html",msg="can't post in chats")
            session["body"]=""
            session["fun"]="False"
            funposts=short_messages.query.filter_by(key=prvt_key, sender_id=me.id).all()
            for i in funposts:
                db.session.delete(i)
                db.session.commit()
    try:
        our_chats=chats.query.order_by(chats.id.desc()).filter_by(key=prvt_key).limit(7)
        our_chats=our_chats[::-1]
        shortchat=short_messages.query.filter_by(key=prvt_key).all()
    except:
        return render_template("message.html",msg="plz give valid input or check code")    
    return render_template("chat.html",name=me,chats=our_chats,frnd=friend,feelings=shortchat,hide=session.get("fun"),body=session.get("body"))






@app.route("/<topic>",methods=["GET","POST"])
def test(topic):

    return redirect("/")



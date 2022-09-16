from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from datetime import timezone
from sqlalchemy.sql import func
from sqlalchemy import MetaData, create_engine



app = Flask(__name__)
app.config.from_object(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.sqlite3'
db = SQLAlchemy(app)
# engine = create_engine('sqlite:///test.sqlite3', echo=True)

# metadata=None
class users(db.Model):
    id=db.Column(db.Integer,primary_key=True)                            #User ID
    username=db.Column(db.String(20), unique=True, nullable=False)       #user name
    password=db.Column(db.String(30), nullable=False)                    #user password
    balance=db.Column(db.Integer, nullable=True, default=0)              #user balance
    post=db.relationship('posts',backref='user')                         #relation#
    topic=db.relationship('channel',backref='user')
    chat=db.relationship('chats',backref='sender')
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
    key=db.Column(db.String,unique=False,nullable=False)                      #Private Key
    sender_id= db.Column(db.Integer, db.ForeignKey('users.id'))             #Sender ID
    data=db.Column(db.String, nullable=False)                               #actuall msg
    time = db.Column(db.DateTime, default=func.now())                       #time

class posts(db.Model):
    id=db.Column(db.Integer,primary_key=True)                               #msg/post ID
    data=db.Column(db.String, nullable=False)                               #actuall msg
    sender_id= db.Column(db.Integer, db.ForeignKey('users.id'))             #User ID
    time = db.Column(db.DateTime, default=func.now())                       #time
    topic=db.relationship('channel',secondary=channel_post,backref=db.backref('posts',lazy='dynamic'))      #Association table->channel_post

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
    else:
        return redirect("/app")




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
                if user.password == password:
                    session["id"]=user.id
                    return  redirect("/")
                return render_template("message.html",msg="incorrect password")
            except:
                return render_template("message.html",msg="Username doesn't exist")

        if operation == "register":
            user = users.query.filter_by(username=name).first()
            if user!=None:
                print(user)
                return render_template("message.html",msg="Username exist")
            user=users(username=name,password=password,balance=0)
            db.session.add(user)
            db.session.commit()
            user = users.query.filter_by(username=name).first()
            session["id"] =user.id
            return  redirect("/")
        if send=="register":
            return render_template("register.html")  
        elif send=="login":
            return redirect("/login")

            
@app.route('/logout',methods=["POST"])    
def logout():
    session["id"]=None
    print(session["id"])
    return redirect("login")


@app.route('/delete/<Channel>' ,methods=["GET"])
def delete_channel(Channel):
    try:
        data=channel.query.filter_by(name=Channel).first()
        post=data.posts
        for i in post:
            db.session.delete(i)
            db.session.commit()
        db.session.delete(data)
        db.session.commit()
        session["channel"]=None
    except:
        return render_template("message.html",msg="no channel exist/can't delete")
    return redirect('/')


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
    
    elif newChannel==None:
        channels=channel.query.all()
        return render_template("user.html",name=user.username,balance=user.balance,tables=channels)
    
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
    return render_template("user.html",name=user.username,balance=user.balance,tables=channels)



@app.route("/channel/<Channel>",methods=["GET","POST"])
def channel_chat(Channel):
    if session.get("id")==None:
        return redirect("/login")
    id=session.get("id")
    post_data=request.form.get("post")
    user = users.query.filter_by(id=id).first()
    name=user
    try:
        current_channel=channel.query.filter_by(name=Channel).first()
        session["channel"]=current_channel.name
        print(session.get("channel"))
    except:
        return render_template("message.html",msg="channel not found")
    if session.get("channel"):
        if post_data!=None:
            
            post=posts(data=post_data,sender_id=user.id)
            post.topic.append(current_channel)
            db.session.add(post)
            db.session.commit()
            print("posted")
                        
        tables=channel.query.all()
        current_channel=channel.query.filter_by(name=Channel).first()
        topic_posts=current_channel.posts

        user=users.query.order_by(users.id).all()
        print("my work is done")
        return render_template("channel_chat.html",name=name,posts=topic_posts,users=user,topic=current_channel,tables=tables)
                
    else:
        return render_template("message.html",msg="channel don't exist")


@app.route("/chat/<frnd>",methods=["GET","POST"])
def chat(frnd):
    if session.get("id")==None:
        return redirect("/login")
    id=session.get("id")
    message=request.form.get("message")
    me=users.query.filter_by(id=id).first()
    friend=users.query.filter_by(username=frnd).first()

#private key
    my_id=me.id
    frnd_id=friend.id
    if my_id<frnd_id:
        prvt_key=str(my_id)+"-"+str(frnd_id)
    elif frnd_id<my_id:
        prvt_key=str(frnd_id)+"-"+str(my_id)
    else:
        prvt_key=str(my_id)+'-'+str(frnd_id)

    if message==None:
#get chats
        try:
            our_chats=chats.query.filter_by(key=prvt_key).all()
        except:
            return render_template("message.html",msg="plz give valid input or check code")    
        return render_template("chat.html",name=me,chats=our_chats,frnd=friend)

# add to table pyare
    try:
        chat=chats(data=message,key=prvt_key,sender_id=my_id)
        db.session.add(chat)
        db.session.commit()
        print("your chat is saved privately")
    except:
        return render_template("message.html",msg="can't send to database")

    return redirect("/chat/"+str(frnd).strip())







@app.route("/test/<topic>",methods=["GET","POST"])
def test(topic):
    ch=channel.query.filter_by(name=topic).first()
    name=ch.user.password
    print(name)
    return "done"



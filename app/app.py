from socket import MsgFlag
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
    id=db.Column(db.Integer,primary_key=True)  #User ID
    username=db.Column(db.String(20), unique=True, nullable=False) #user name
    password=db.Column(db.String(30), nullable=False) #user password
    balance=db.Column(db.Integer, nullable=True, default=0) #user balance
    post=db.relationship('posts',backref='user') #relation#
    def __init__(self, username, password, balance):
        self.username=username
        self.password=password
        self.balance=balance

class topic_id(db.Model):
    id=db.Column(db.Integer,primary_key=True) 
    name=db.Column(db.String, nullable=False,unique=True)
    topic=db.relationship('posts',backref='topic')

class posts(db.Model):
    id=db.Column(db.Integer,primary_key=True) #msg/post ID
    data=db.Column(db.String, nullable=False) #actuall msg
    sender_id= db.Column(db.Integer, db.ForeignKey('users.id')) #User ID
    topicid=db.Column(db.Integer, db.ForeignKey('topic_id.id')) #topic ID
    time = db.Column(db.DateTime, default=func.now()) #time



# SQLALCHEMY_TRACK_MODIFICATIONS = True

db.create_all()


#Session
app.config["SESSION_PERMANENT"]=False
app.config["SESSION_TYPE"]="filesystem"
Session(app)



# Database
superuser=[]
couponbase=[]
namedata=[]
passdata=[]
database=[]
# database=[{"titanic":50,"hacking":550},{"nudes":"free"},{},{},...]
balancedata=[]
reffral_code={
    "JAIHO":100,
    "HACKER":69
}

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
    if session.get("topic")!=None:
        return redirect("/user/"+str(session.get("topic")))
    else:
        return redirect("/user")




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

@app.route('/reset',methods=["POST"])    
def reset():
    try:
        post= posts.query.all()
        for i in post:
            print(i)
            db.session.delete(i)
            db.session.commit()
        user = users.query.all()
        for i in user:
            db.session.delete(i)
            db.session.commit()
        data = topic_id.query.all()
        for i in data:
            print(i)
            db.session.delete(i)
            db.session.commit()
        print("delete")
        return redirect("/login")
    except:
        return render_template("message.html",msg="can't delete plz check your data")


@app.route("/user",methods=["GET","POST"])
def user():
    if session.get("id")==None:
        return redirect("/login") 
    session["topic"]=None   
    id=session.get("id")
    user=users.query.filter_by(id=id).first()
    name=user.username
    balance=user.balance
    topic=request.form.get("topic_name")
    tables=topic_id.query.all()
    if topic==None:
        return render_template("user.html",name=name,balance=balance,tables=tables)
    try:
        topic=topic_id(name=topic)
        db.session.add(topic)
        db.session.commit()
        print("sucess")
    except:
        return render_template("message.html",msg="can't add to topic id")
    try:
        tables=topic_id.query.all()
        return render_template("user.html",name=name,balance=balance,tables=tables)
    except:
        print("can't show topics id")



@app.route("/user/<topic>",methods=["GET","POST"])
def todo(topic):
    if session.get("id")==None:
        return redirect("/login")
    id=session.get("id")
    post_data=request.form.get("post")
    Topic=str(topic)
    user = users.query.filter_by(id=id).first()
    name=user.username
    try:
        topic=topic_id.query.filter_by(name=Topic).first()
        session["topic"]=topic.name
        print(session.get("topic"))
    except:
        return render_template("message.html",msg="topic not found")
    if session.get("topic"):
        if post_data!=None:
            try:
                post=posts(data=post_data,sender_id=user.id,topicid=topic.id)
                db.session.add(post)
                db.session.commit()
                print("posted")
            except:
                return render_template("message.html",msg="not added to table/topic")
        data=posts.query.filter_by(topicid=topic.id).order_by(posts.time.desc()).all()
        user=users.query.order_by(users.id).all()
        return render_template("todo.html",name=name,mydata=data,user=user,topic=topic)
                
        return render_template("message.html",msg="topic don't exist")
    else:
        return render_template("message.html",msg="stop messing with me")
@app.route("/shop",methods=["GET","POST"])
def shop():
    if session.get("id")==None:
        return redirect("/login")
    return render_template("shop.html")

@app.route("/test",methods=["GET","POST"])
def test():
    # print(MetaData)
    return "done"
from socket import MsgFlag
from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from datetime import timezone
from sqlalchemy.sql import func



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.sqlite3'
db = SQLAlchemy(app)


class users(db.Model):
    id=db.Column(db.Integer,primary_key=True)  #User ID
    username=db.Column(db.String(20), unique=True, nullable=False) #user name
    password=db.Column(db.String(30), nullable=False) #user password
    balance=db.Column(db.Integer, nullable=True, default=0) #user balance
    post=db.relationship('general_topic',backref='user') #relation#

class general_topic(db.Model):
    id=db.Column(db.Integer,primary_key=True) #msg/post ID
    data=db.Column(db.String, nullable=False) #actuall msg
    sender_id= db.Column(db.Integer, db.ForeignKey('users.id')) #User ID
    time = db.Column(db.DateTime, default=func.now()) #time


# SQLALCHEMY_TRACK_MODIFICATIONS = False

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
@app.route('/',methods=["GET","POST"])
def index():
    if session.get("id")==None:
        return redirect("/login")
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
            user=users(username=name,password=password)
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
        user = users.query.order_by(users.id.asc()).all()
        for i in user:
            db.session.delete(i)
            db.session.commit()
        data = general_topic.query.order_by(general_topic.id.asc()).all()
        for i in data:
            print(i)
            db.session.delete(i)
            db.session.commit()
        tables=db.engine.table_names()   
        for table in tables:
            

        return redirect("/login")
    except:
        return redirect("/login")


@app.route("/user",methods=["GET","POST"])
def user():
    if session.get("id")==None:
        return redirect("/login")    
    id=session.get("id")
    user=users.query.filter_by(id=id).first()
    name=user.username
    balance=user.balance
    tables=db.engine.table_names()   
    if request.form.get("topic_name") ==None:
        return render_template("user.html",name=name,balance=balance,tables=tables)
    
    topic=request.form.get("topic_name")
    if str(topic) not in table:
        try:
            class topic(db.Model):
                __tablename__=(topic)
                id=db.Column(db.Integer,primary_key=True) #msg/post ID
                data=db.Column(db.String, nullable=False) #actuall msg
                sender_id= db.Column(db.Integer, db.ForeignKey('users.id')) #User ID
                time = db.Column(db.DateTime, default=func.now()) #time
            db.create_all()
        except:
            return render_template("message.html",msg="can't create table")
        table=db.engine.table_names()   
        return render_template("user.html",name=name,balance=balance,tables=table)
    else:
        return render_template("message.html",msg="topic already exist")




@app.route("/user/<topic>",methods=["GET","POST"])
def todo(topic):
    if session.get("id")==None:
        return redirect("/login")
        
    id=session.get("id")
    post_data=request.form.get("post")
    user = users.query.filter_by(id=id).first()
    name=user.username
    if topic=="general_topic":  
        if post_data!=None:
            try:
                post=general_topic(data=post_data,sender_id=user.id)
                db.session.add(post)
                db.session.commit()
            except:
                return render_template("message.html",msg="lol")
        data=general_topic.query.order_by(general_topic.time.asc()).all()
        user=users.query.order_by(users.id).all()
        return render_template("todo.html",name=name,mydata=data,user=user)
    else:
        return render_template("message.html",msg="not a good table")


@app.route("/shop",methods=["GET","POST"])
def shop():
    if session.get("id")==None:
        return redirect("/login")
    return render_template("shop.html")

@app.route("/test",methods=["GET","POST"])
def test():
    user = users.query.all()
    users=[]
    for i in user:
        users.append(i.username)
        users.append(i.password)
    return render_template("test.html",user=users)
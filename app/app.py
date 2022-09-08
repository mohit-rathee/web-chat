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
    # post=db.relationship('general_topic',backref='user') #relation#
    def __init__(self, username, password, balance):
        self.username=username
        self.password=password
        self.balance=balance

class topic_id(db.Model):
    id=db.Column(db.Integer,primary_key=True) 
    name=db.Column(db.String, nullable=False,unique=True)


# class general_topic(db.Model):
#     id=db.Column(db.Integer,primary_key=True) #msg/post ID
#     data=db.Column(db.String, nullable=False) #actuall msg
#     sender_id= db.Column(db.Integer, db.ForeignKey('users.id')) #User ID
#     time = db.Column(db.DateTime, default=func.now()) #time



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
        user = users.query.order_by(users.id.asc()).all()
        # for i in user:
        #     db.session.delete(i)
        #     db.session.commit()
        # data = general_topic.query.order_by(general_topic.id.asc()).all()
        for i in data:
            print(i)
            db.session.delete(i)
            db.session.commit()
        print("delete")
        tables=db.engine.table_names()   
        # for t in tables:
            #delete table
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
    top=str(topic)
    if str(topic) not in tables:
        try:
            
            class post(db.Model):
                __tablename__=str(topic)
                id=db.Column(db.Integer,primary_key=True) #msg/post ID
                data=db.Column(db.String, nullable=False) #actuall msg
                sender_id= db.Column(db.Integer, db.ForeignKey('users.id')) #User ID
                time = db.Column(db.DateTime, default=func.now()) #time
                def __init__(self, data, time, sender_id): 
                    self.data=data
                    self.time=time
                    self.sender_id=sender_id
            db.create_all()
        except:
                return render_template("message.html",msg="cant relates")
        try:
            topic=topic_id(name=top)
            db.session.add(topic)
            db.session.commit()
            print("sucess")
        except:
            return render_template("message.html",msg="can't add to topic id")

        tables=db.engine.table_names()   
        return render_template("user.html",name=name,balance=balance,tables=tables)
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
    tables=db.engine.table_names() 
    if topic in tables:
        try:
            topic = topic_id.query.filter_by(name=topic).first()
            print(topic.name)
            print(topic.post.data)
        except:
            return render_template("message.html",msg="ghapla")
        
        return render_template("message.html",msg=user.name+" exist")
    #     if table==topic:
    #     # if topic=="general_topic":  
    #         if post_data!=None:
    #             try:
    #                 post=topic(data=post_data,sender_id=user.id)
    #                 db.session.add(post)
    #                 db.session.commit()
    #             except:
    #                 return render_template("message.html",msg="not added to table/topic")
    #         data=topic.query.order_by(topic.time.asc()).all()
    #         user=users.query.order_by(users.id).all()
    #         return render_template("todo.html",name=name,mydata=data,user=user)
    #     else:
    #         return render_template("message.html",msg="not a good table")
    # return render_template("message.html",msg="not a good table")

@app.route("/shop",methods=["GET","POST"])
def shop():
    if session.get("id")==None:
        return redirect("/login")
    return render_template("shop.html")

@app.route("/test",methods=["GET","POST"])
def test():
    # print(MetaData)
    return "done"
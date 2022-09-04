from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.sqlite3'
db = SQLAlchemy(app)


class Users(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(20), unique=True, nullable=False)
    password=db.Column(db.String(30), nullable=False)
    balance=db.Column(db.Integer, nullable=True, default=0)
    superusers=db.relationship('Superusers',backref='user')

class Superusers(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('users.id'))


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
                user = Users.query.filter_by(username=name).first()
                if user.password == password:
                    session["id"]=user.id
                    return  redirect("/")
                return render_template("failure.html",error="incorrect password")
            except:
                return render_template("failure.html",error="Username doesn't exist")

        if operation == "register":
            user = Users.query.filter_by(username=name).first()
            if user!=None:
                return render_template("failure.html",error="Username exist")
            user=Users(username=name,password=password)
            db.session.add(user)
            db.session.commit()
            user = Users.query.filter_by(username=name).first()
            session["id"] =user.id
            if power=="super":
                superuser=Superusers(user_id=user.id)
                db.session.add(superuser)
                db.session.commit()
            
            
        if send=="register":
            return render_template("register.html")  
        elif send=="login":
            return redirect("/login")

            
@app.route('/logout',methods=["POST"])    
def logout():
    session["id"]=None
    print(session["id"])
    return redirect("login")
    
@app.route("/user",methods=["GET","POST"])
def user():
    if session.get("id")==None:
        return redirect("/login")    
    id=session.get("id")
    user=Users.query.filter_by(id=id).first()
    name=user.username
    balance=user.balance
    superuser=Superusers.query.filter_by(user_id=id).first()

        # if (request.form.get("new_coupon") and request.form.get("new_value")):
        #     couponbase[x][str(request.form.get("new_coupon"))]=int(request.form.get("new_value"))
        #     print(couponbase)
        #     return render_template("user.html",name=name,balance=balance,superuser=True,coupons=couponbase[x])
        # if request.form.get("remove_coupon"):
        #     couponbase[x].pop(str(request.form.get("remove_coupon")))
    if superuser!=None:
        return render_template("user.html",name=name,balance=balance,superuser=True,sname=superuser.user.username)
    return render_template("user.html",name=name,balance=balance,superuser=False)



@app.route("/user/to-do",methods=["GET","POST"])
def todo():
    if session.get("id")==None:
        return redirect("/login")
    id=session.get("id")
    if not id in superuser:
        if request.form.get("item")==None:
            return render_template('todo.html',name=namedata[id],data=database[id],superuser=False)
        item=request.form.get("item")
        database[id][str(item)]="free"
        print(database[id])
        return render_template('todo.html',name=namedata[id],data=database[id],superuser=False)
    if request.form.get("item")==None:
        return render_template('todo.html',name=namedata[id],data=database[id],superuser=True)
    item=request.form.get("item")
    if request.form.get("value"):
        value=request.form.get("value")
        database[id][str(item)]=value
        print(database[id])
        return render_template('todo.html',name=namedata[id],data=database[id],superuser=True)
    database[id][str(item)]="free"
    return render_template('todo.html',name=namedata[id],data=database[id],superuser=True)
    
    

@app.route("/shop",methods=["GET","POST"])
def shop():
    if session.get("id")==None:
        return redirect("/login")
    return render_template("shop.html")

@app.route("/test",methods=["GET","POST"])
def test():
    user = Users.query.all()
    users=[]
    for i in user:
        users.append(i.username)
        users.append(i.password)
    return render_template("test.html",user=users)
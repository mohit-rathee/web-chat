from ast import Try
from crypt import methods
from operator import indexOf
from flask import Flask, render_template, request, redirect, session, url_for
from flask_session import Session
app = Flask(__name__)

#Session
app.config["SESSION_PERMANENT"]=False
app.config["SESSION_TYPE"]="filesystem"
Session(app)

# Database
namedata=["guest","mohit"]
passdata=["123","rathee"]
database=[["first work","second work","third work"],["sdhgkhg","sdnkjjsdkg"]]

# Routes
@app.route('/',methods=["GET","POST"])
def index():
    if not session.get("name"):
        return redirect("/login")
    return render_template("home.html",name=session.get("name"))
    

@app.route('/login',methods=["GET","POST"])
def login():
    if request.method=="GET":
        return render_template("login.html")
    if request.method=="POST":
        item=request.form.get("username")
        password=request.form.get("password")
        operation=request.form.get("operation")
        if operation == "login":
            try:
                index=namedata.index(item)
            except ValueError:
                return render_template("failure.html",error="Username doesn't exist")
            if passdata[index] == password:
                session["id"] = index
                session["name"] = item
                session["password"] = password
                return  redirect("/")
            return render_template("failure.html",error="incorrect password")
            

        if operation == "register":
            for i in namedata:
                if item == i:
                    return render_template('failure.html',error="username already exists")
            namedata.append(item)
            passdata.append(password)  
            database.append([])
            print(namedata)
            session["name"] = item
            session["password"] = password
            session["id"] =int(len(database))-1
            return  redirect("/")
        
            
@app.route('/logout',methods=["POST"])    
def logout():
    session["name"]=None
    session["password"]=None
    session["id"]=None
    return redirect("login")
    
@app.route("/user",methods=["GET","POST"])
def user():
    if not session.get("name"):
        return redirect("/login")
    name=session.get("name")
    password=session.get("password")
    id=session.get("id")
    if request.form.get("note")==None:
        return render_template('user.html',name=name,data=database[id])
    note=request.form.get("note")
    database[id].append(note)
    return render_template('user.html',name=name,data=database[id])
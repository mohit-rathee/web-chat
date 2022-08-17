from flask import Flask, render_template, request, redirect, session, url_for
from flask_session import Session
app = Flask(__name__)

#Session
app.config["SESSION_PERMANENT"]=False
app.config["SESSION_TYPE"]="filesystem"
Session(app)

# Database
namedata=["heck","guest","mohit"]
passdata=["heck","123","rathee"]
database=[["first work","second work","third work"],["sdhgkhg","sdnkjjsdkg"]]
balancedata=[]
couponbase={
    "JAIHO":100,
    "HACKER":69
}

# Routes
@app.route('/',methods=["GET","POST"])
def index():
    if not session.get("id"):
        return redirect("/login")
    id=session.get("id")
    name=namedata[id]
    return render_template("home.html",name=name)
    

@app.route('/login',methods=["GET","POST"])
def login():
    if request.method=="GET":
        return render_template("login.html")
    if request.method=="POST":
        name=request.form.get("username")
        password=request.form.get("password")
        operation=request.form.get("operation")
        if operation == "login":
            try:
                id=namedata.index(name)
                print(id)
            except ValueError:
                return render_template("failure.html",error="Username doesn't exist")
            if passdata[id] == password:
                session["id"]=id
                return  redirect("/")
            return render_template("failure.html",error="incorrect password")
            

        if operation == "register":
            for i in namedata:
                if name == i:
                    return render_template('failure.html',error="username already exists")
            namedata.append(name)
            passdata.append(password)  
            database.append([])
            session["id"] =int(len(database))-1
            return  redirect("/")
        
            
@app.route('/logout',methods=["POST"])    
def logout():
    session["id"]=None
    return redirect("login")
    
@app.route("/user",methods=["GET","POST"])
def user():
    if not session.get("id"):
        return redirect("/login")
    id=session.get("id")
    name=namedata[id]
    if request.form.get("note")==None:
        return render_template('user.html',name=name,data=database[id])
    note=request.form.get("note")
    database[id].append(note)
    print(database[id])
    return render_template('user.html',name=name,data=database[id])
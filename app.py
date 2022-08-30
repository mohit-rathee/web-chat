from flask import Flask, render_template, request, redirect, session
from flask_session import Session
app = Flask(__name__)

#Session
app.config["SESSION_PERMANENT"]=False
app.config["SESSION_TYPE"]="filesystem"
Session(app)

# Database
superuser=[0]
namedata=[]
passdata=[]
database=[]
balancedata=[]
couponbase={
    "JAIHO":100,
    "HACKER":69
}

# Routes
@app.route('/',methods=["GET","POST"])
def index():
    if session.get("id")==None:
        return redirect("/login")
    return redirect("/user")


def couponchecker(id,coupon):
    for Coupon in couponbase:
        if Coupon == coupon:
            balancedata[id]+=couponbase[Coupon]

@app.route('/login',methods=["GET","POST"])
def login():
    if request.method=="GET":
        return render_template("login.html")
    if request.method=="POST":
        name=request.form.get("username")
        password=request.form.get("password")
        operation=request.form.get("operation")
        coupon=request.form.get("coupon")
        if operation == "login":
            try:
                id=namedata.index(name)
                print(id)
            except ValueError:
                return render_template("failure.html",error="Username doesn't exist")
            if passdata[id] == password:
                session["id"]=id
                couponchecker(id,coupon)
                return  redirect("/")
            return render_template("failure.html",error="incorrect password")
            

        if operation == "register":
            for i in namedata:
                if name == i:
                    return render_template('failure.html',error="username already exists")
            id=int(len(namedata))
            namedata.append(name)
            passdata.append(password)  
            database.append([])
            balancedata.append(0.00)
            print(id)
            session["id"] =id
            couponchecker(id,coupon)
            return  redirect("/")
        
            
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
    name=namedata[id]
    balance=balancedata[id]
    if id in superuser:
        if (request.form.get("new_coupon") and request.form.get("new_value")):
            couponbase[str(request.form.get("new_coupon"))]=int(request.form.get("new_value"))
            print(couponbase)
            return render_template("user.html",name=name,balance=balance,superuser=True,coupons=couponbase)
        if request.form.get("remove_coupon"):
            couponbase.pop(str(request.form.get("remove_coupon")))
        return render_template("user.html",name=name,balance=balance,superuser=True,coupons=couponbase)
    return render_template("user.html",name=name,balance=balance,superuser=False)



@app.route("/user/to-do",methods=["GET","POST"])
def todo():
    if session.get("id")==None:
        return redirect("/login")
    id=session.get("id")
    if request.form.get("note")==None:
        return render_template('todo.html',name=namedata[id],data=database[id])
    note=request.form.get("note")
    database[id].append(note)
    print(database[id])
    return render_template('todo.html',name=namedata[id],data=database[id])



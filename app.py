from flask import Flask, render_template, request, redirect, session
from flask_session import Session
app = Flask(__name__)

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


def couponchecker(id,coupon):
    for Coupon in reffral_code:
        if Coupon == coupon:
            balancedata[id]+=reffral_code[Coupon]

@app.route('/login',methods=["GET","POST"])
def login():
    if request.method=="GET":
        return render_template("login.html")
    if request.method=="POST":
        name=request.form.get("username")
        password=request.form.get("password")
        operation=request.form.get("operation")
        coupon=request.form.get("coupon")
        power=request.form.get("power")
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
            database.append({})
            if power=="super":
                superuser.append(id)
                couponbase.append({})
            balancedata.append(0.00)
            print(id)
            print(superuser)
            print(couponbase)
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
        try:
            x=superuser.index(id)
        except ValueError:
            return render_template("failure.html",error="Superuser doesn't exist")
        if (request.form.get("new_coupon") and request.form.get("new_value")):
            couponbase[x][str(request.form.get("new_coupon"))]=int(request.form.get("new_value"))
            print(couponbase)
            return render_template("user.html",name=name,balance=balance,superuser=True,coupons=couponbase[x])
        if request.form.get("remove_coupon"):
            couponbase[x].pop(str(request.form.get("remove_coupon")))
        return render_template("user.html",name=name,balance=balance,superuser=True,coupons=couponbase[x])
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
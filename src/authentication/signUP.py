from flask import session
from .. import server
from ..database.models import users
from passlib.hash import sha256_crypt

def registrationlogic(name,password,serverList):
    pswdHash=""
    myserver=[]
    #serverList=request.form.getlist("server[]")
    if len(serverList)==0:
        return render_template("message.html",msg="Select atleast one server", goto="/login")
    for srvr in serverList:
        isRegisterAllowed = server[srvr].query(admin).filter_by(id=3).first()
        #if not int(isRegisterAllowed.value):
            #return render_template("message.html",msg="Registration not allowed on this server", goto="/login")
        user=server[srvr].query(users).filter_by(username=name).first()
        if user!=None:
            if sha256_crypt.verify(str(name+password), user.password):
                pswdHash=user.password
                session[srvr]=user.id
                myserver.append(srvr)
                session["name"]=user.username
            #else:
                #return render_template("message.html",msg="Username exist",goto="/login")
    if not pswdHash:
        pswdHash=sha256_crypt.encrypt(str(name+password))
    for srvr in serverList:
        if srvr not in myserver:
            user=users(username=name,password=pswdHash)
            server[srvr].add(user)
            server[srvr].commit()
            session[srvr]=user.id
            session["name"]=user.username
            myserver.append(srvr)
    session["myserver"]=myserver[:]
    session["server"]=myserver[0]
    #if len(serverList)==len(server):
        #return redirect("/channels")
    #done=loginlogic(name, password)
    #if done:
     #   return redirect("/channels")
    #else:
     #   return render_template("message.html",msg="YOUR OLD PASSWORD IS UPDATED WITH NEWONE",goto="/channels")


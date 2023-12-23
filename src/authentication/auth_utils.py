from flask import session
from .. import server
from ..database.models import users
import bcrypt

# I confess my loginlogic may be bad, but their will be issues with other logic too.

def loginlogic(name,password):
    myServers=[]
    for srvr in server.keys():
        user = server[srvr].query(users).filter_by(username=name).first()
        if user!=None:
            if bcrypt.checkpw(password.encode('utf-8'), user.password):
                session["name"]=name
                session[srvr]=user.id
                myServers.append(srvr)
    if len(myServers)==0:
            return False
    session["myserver"]=myServers
    return True

def registrationlogic(name,password,serverList):
    pswdHash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    myserver=[]
    pending=[]
    result = True
    for srvr in serverList:
        #isRegisterAllowed = server[srvr].query(admin).filter_by(id=3).first()
        #if not int(isRegisterAllowed.value):
            #return render_template("message.html",msg="Registration not allowed on this server", goto="/login")
        user=server[srvr].query(users).filter_by(username=name).first()
        if user!=None: # login if already registrated
            if bcrypt.checkpw(pswdHash,user.password):
                pswdHash=user.password
                session[srvr]=user.id
                myserver.append(srvr)
                session["name"]=user.username
            else:
                result = False
                pending.append(srvr) #username is occupied
        else:
            user=users(username=name,password=pswdHash)
            server[srvr].add(user)
            server[srvr].commit()
            session[srvr]=user.id
            session["name"]=user.username
            myserver.append(srvr)
    session["myserver"]=myserver
    return result,pending


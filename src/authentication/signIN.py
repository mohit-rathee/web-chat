from flask import session
from .. import server
from ..database.models import users
from passlib.hash import sha256_crypt

# I confess my loginlogic may be bad, but their will be issues with other logic too.

def loginlogic(name,password,myServer):
    #myServer=session.get("myserver")
    pswdHash=None
    if myServer!=None:
        session["server"]=myServer[0]
        user=server[myServer[0]].query(users).filter_by(id=session.get(myServer[0])).first()
        pswdHash=user.password
    else:
        myServer=[]
    undone=[]
    for srvr in server.keys():
        if srvr not in myServer:
            user = server[srvr].query(users).filter_by(username=name).first()
            if user!=None:
                if pswdHash==None:
                    if sha256_crypt.verify(str(name+password), user.password):
                        pswdHash=user.password
                        session["server"]=srvr
                        session["name"]=name
                        session[srvr]=user.id
                        myServer.append(srvr)
                    else:
                        undone.append(srvr)
                else:
                    if pswdHash != user.password:
                        if sha256_crypt.verify(str(name+password), user.password):
                            user.password=pswdHash
                            server[srvr].commit()
                        else:
                            user.password=pswdHash
                            server[srvr].commit()
                    myServer.append(srvr)
                    session[srvr]=user.id
    if len(myServer)==0:
            return False
    for srvr in undone:
        user = server[srvr].query(users).filter_by(username=name).first()
        user.password=pswdHash
        server[srvr].commit()
        myServer.append(srvr)
        session[srvr]=user.id
    session["myserver"]=myServer[:]
    return True


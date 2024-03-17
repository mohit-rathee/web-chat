from flask import session
from .. import server
from ..database.database_utils import check_credential, add_user, get_default_role
import bcrypt

# I confess my loginlogic may be bad, but their will be issues with other logic too.

def loginlogic(name,password):
    myServers=[]
    pswd = password.encode('utf-8')
    for srvr in server.keys():
        credentials = check_credential(srvr,name,pswd)
        if credentials:
            myServers.append(srvr)
            session["name"]=credentials[0]
            session[srvr]=credentials[1]
    if len(myServers)==0:
            return False
    session["myserver"]=myServers
    return True

def registrationlogic(name,password,serverList):
    pswd = password.encode('utf-8')
    pswdHash = bcrypt.hashpw(pswd, bcrypt.gensalt())
    myserver=[]
    for srvr in serverList:
        credentials = check_credential(srvr,name,pswd)
        if credentials != None and credentials !=[False]: # credentials matched
            myserver.append(srvr)
            session["name"]=credentials[0]
            session[srvr]=credentials[1]
        elif credentials == [False]:
            continue # password not matched
        else:
            default_role = get_default_role(srvr)
            credentials = add_user(srvr,name,pswdHash,default_role)
            session[srvr] = credentials[0]
            session["name"] = credentials[1]
            myserver.append(srvr)

    if len(myserver)!=0:
        session["myserver"]=myserver
        return True
    else:
        return False


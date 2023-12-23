from .. import app, server, db_dir, os
from ..authentication.auth_utils import loginlogic, registrationlogic
from ..database.database_utils import create_conn
from flask import render_template, redirect, session, request, send_file, make_response, Blueprint
from werkzeug.utils import secure_filename

# Create a Blueprint named 'routes'
routes = Blueprint("routes", __name__, 
                   template_folder="../../templates")

    
@routes.route('/',methods=["GET","POST"])
def index():
    if request.method=="GET":
        if session.get("name")==None:
            return redirect("/login")
        else:
            return redirect("/channels")
    session.clear()
    return redirect("/")


@routes.route('/create',methods=["POST"])
def createdb():
    name=str(request.form.get("name"))
    if name in server or "/" in name:
        return render_template("message.html",
                               msg="select a unique and valid name.",
                               goto="/")
    
    db_uri = f'sqlite:///db/{secure_filename(name)}.sqlite3'
    # Creating a connection.
    if create_conn(name,db_uri):
        return redirect("/login")
    else:
        session.clear()
        os.remove("db/"+name+".sqlite3")
        return render_template("message.html",msg="Can't create your server.",goto="/login")


@routes.route('/upload',methods=["POST"])
def upload_db():
    files=request.files.getlist('files')
    success = True
    for file in files:
        name = str(file.filename)
        fileName=secure_filename(name)
        filePart = fileName.split('.')
        if not file or filePart[1]!="sqlite3" or filePart[0] in server:
            return render_template("message.html",msg="select a valid database file (*.sqlite3) with unique name.",goto="/login")
        fullPath = os.path.join(db_dir,fileName)
        file.save(fullPath)
        name=filePart[0]
        db_uri = f'sqlite:///db/{secure_filename(name)}.sqlite3'
        session.clear()
        if not create_conn(name,db_uri):
            success = False
    if success:
        return redirect("/login")
    else:
        return render_template("message.html",msg="NOT A VALID DATABASE",goto="/login")

@routes.route("/channels",methods=["GET"])
def channel_chat():
    if not session.get("name"):
        return redirect("/login")
    name=session.get("name")
    myserver=session.get("myserver")
    return render_template("channel_chat.html",name=name,myservers=myserver)

@routes.route('/download/<server>',methods=["GET"])
def download_database(server):
    if app.config['SQLALCHEMY_BINDS'].get(str(server)):
        path =str(app.config['SQLALCHEMY_BINDS'][str(server)]).rsplit("///")[1]
        return send_file(path, as_attachment=True)
    else:
        return make_response('Not Found',404)


@routes.route('/login',methods=["GET","POST"])
def login():
    # REDIRECT IF LOGGED IN
    if request.method=="GET":
        if session.get("name")==None:
            allServers=[]
            for srvr in server.keys():
                allServers.append(srvr)
            return render_template("login.html",servers=allServers)
        else:
            return redirect("/channels")
    #else: When method == POST
    session.clear()
    name=str(request.form.get("username"))
    password=str(request.form.get("password"))
    operation=request.form.get("operation")
    if operation == "login":
        if loginlogic(name, password):
            return redirect("/channels")
        else:
            return render_template("message.html",
                msg="Username or password are incorrect",
                goto="/login")
    elif operation == "register":
        serverList = request.form.getlist("server[]")
        if len(serverList)==0:
            return render_template("message.html",
                                   msg="Select at least one server")
        [result,pending] = registrationlogic(name,password,serverList)
        if result:
            return redirect("/channels")
        else:
            if session.get('myservers'):
                return redirect("/channels")
            else:
                return render_template("message.html",
                    msg="Username exists in all servers.\n Find a unique name.",
                    goto="/login")
    else:
        return redirect('/login')



import bcrypt
from bidict import bidict
from .. import app, server, db_dir, os, engine, rooms, base, tables
from ..authentication.auth_utils import loginlogic, registrationlogic
from ..database.database_utils import create_connection, create_server_status, add_user
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
    db_name=str(request.form.get("name"))
    admin_name=str(request.form.get("admin_name"))
    admin_pswd=str(request.form.get("admin_password"))

    # remove this check later
    if db_name in server or "/" in db_name:
        return render_template("message.html",
                               msg="select a unique and valid name.",
                               goto="/")
    
    db_uri = f'sqlite:///db/{secure_filename(db_name)}.sqlite3'
    # Creating a connection.
    connection_status = create_connection(db_name,db_uri)
    if connection_status==[False]:
        status = create_server_status(db_name,db_name,desc="")
        #update memory and add admin user.
        db_uuid = status["uuid"]
        tables[db_uuid]={'Len':0,"Name":db_name}
        base[db_uuid]=base.pop(db_name)
        engine[db_uuid]=engine.pop(db_name)
        server[db_uuid]=server.pop(db_name)
        rooms[db_uuid]=bidict({})

        admin_hashed_pswd = bcrypt.hashpw(admin_pswd.encode('utf-8'), bcrypt.gensalt())
        add_user(db_uuid,admin_name,admin_hashed_pswd,1) # Added to admin role
    else:
        session.clear()
        os.remove("db/"+db_name+".sqlite3")
        return render_template("message.html",msg="Can't create your server.",goto="/login")
    return redirect("/login")


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
        if not create_connection(name,db_uri):
            success = False
    if success:
        return redirect("/login")
    else:
        return render_template("message.html",msg="NOT A VALID DATABASE",goto="/login")

@routes.route("/channels",methods=["GET"])
def channel_chat():
    myservers = session.get("myserver")
    if not myservers or not session.get("name"):
        return redirect("/login")
    name=session.get("name")
    my_server_names={uuid : tables[uuid]["Name"] for uuid in myservers}
    return render_template("channel_chat.html",name=name,myservers=my_server_names)

@routes.route('/download/<server>',methods=["GET"])
def download_database(srvr):
    for key in server.keys():
        if tables[key]["Name"]==srvr and session.get(key):
            path =str(server.get(srvr)).rsplit("///")[1]
            return send_file(path, as_attachment=True)
    else:
        return make_response('Not Found',404)


@routes.route('/login',methods=["GET","POST"])
def login():
    # REDIRECT IF LOGGED IN
    if request.method=="GET":
        if session.get("name")==None:
            allServers={uuid : tables[uuid]["Name"] for uuid in server.keys()}
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
        if registrationlogic(name,password,serverList):
            return redirect("/channels")
        else:
            return render_template("message.html",
                msg="Username exists in all servers.\n Find a unique name.",
                goto="/login")
    else:
        return redirect('/login')



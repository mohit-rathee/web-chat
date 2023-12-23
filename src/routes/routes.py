from .. import app, server
from ..authentication.signIN import loginlogic
from ..database.database_utils import create_conn
from flask import render_template, redirect, session, request, send_file, make_response, Blueprint
from werkzeug.utils import secure_filename

# Create a Blueprint named 'routes'
routes = Blueprint("routes", __name__, template_folder="../../templates")

@routes.route('/create',methods=["POST"])
def createdb():
    name=str(request.form.get("name"))
    if " " in name:
        return render_template("message.html",msg="Don't use spaces", goto="/login")
    if name in server or "/" in name:
        return render_template("message.html",msg="select a unique and valid name.",goto="/")
    db_uri = f'sqlite:///db/{name}.sqlite3'

    create_conn(name,db_uri)
    # Creating a connection.
    return redirect("/login")

@routes.route('/upload',methods=["POST"])
def upload_db():
    files=request.files.getlist('files')
    for file in files:
        filename=(secure_filename(file.filename).split("."))
        if not file or filename[1]!="sqlite3" or filename[0] in server:
            return render_template("message.html",msg="select a valid database file (*.sqlite3) with unique name.",goto="/login")
        file.save(os.path.join(uploads_dir,secure_filename(file.filename)))
        name=filename[0]
        app.config['SQLALCHEMY_BINDS'][name] ="sqlite:///"+str(os.path.join(uploads_dir,secure_filename(file.filename)))
        create_conn(name,app.config['SQLALCHEMY_BINDS'][name])
        session.clear()
    return redirect("/login")

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
    else:
        session.clear()
        name=str(request.form.get("username"))
        password=str(request.form.get("password"))
        operation=request.form.get("operation")
        if operation == "login":
            done=loginlogic(name, password,[])
            if done:
                return redirect("/channels")
            else:
                return render_template("message.html",msg="Username or password are incorrect",goto="/login")

@routes.route('/',methods=["GET","POST"])
def index():
    if request.method=="GET":
        if session.get("name")==None:
            return redirect("/login")
        else:
            return redirect("/channels")
    session.clear()
    return redirect("/")

@routes.route("/channels",methods=["GET"])
def channel_chat():
    if not session.get("name"):
        return redirect("/login")
    name=session.get("name")
    myserver=session.get("myserver")
    curr=session.get("server")
    id=session.get(curr)
    return render_template("channel_chat.html",name=name,id=id,server=curr,myservers=myserver)

@routes.route('/download/<server>',methods=["GET"])
def download_database(server):
    if app.config['SQLALCHEMY_BINDS'].get(str(server)):
        path =str(app.config['SQLALCHEMY_BINDS'][str(server)]).rsplit("///")[1]
        return send_file(path, as_attachment=True)
    else:
        return make_response('Not Found',404)



from .. import server, socketio, app, media_dir
from . import mediaHash
from flask import request, make_response, session, send_file, Blueprint
from ..database.models import media
import json, os, uuid, hashlib

medias = Blueprint("medias",__name__)

# Filename will be changed (from: uuid ==> hash)
def uploadSuccess(unique_id,file_hash):
    curr=mediaHash[unique_id][3]
    dbSession=server[curr]
    check=dbSession.query(media).filter_by(hash=file_hash).first()
    if check==None:
        data=mediaHash[unique_id]
        name=[data[1],data[2]] #store only name & typ 
        Media=media(hash=file_hash,name=json.dumps(name))
        dbSession.add(Media)
        dbSession.commit()
        os.rename(media_dir+"/"+unique_id,media_dir+"/"+file_hash) #file saved for the first time.
        socketio.emit("media",[curr,Media.id,Media.hash,name],to=curr)
        return Media.id
    elif not os.path.exists(media_dir+"/"+file_hash): # Previously uploaded file saved.
        os.rename(media_dir+"/"+unique_id,media_dir+"/"+file_hash)
        return check.id
    else:
        os.remove(media_dir+"/"+unique_id) # duplicate file detected.
        return 0
@app.route("/media",methods=["POST"])
def handel_media():
    unique_id=request.form.get('uuid')
    if unique_id:
        # for big files.
        chunk=request.files['chunk'].read()
        hasher = mediaHash[unique_id][0]
        hasher.update(chunk)
        with open(media_dir+"/"+unique_id,"ab") as file:
            file.write(chunk)
        if not request.form.get('dN'):
            return "1"
        file_hash=hasher.hexdigest()
        data = uploadSuccess(unique_id,file_hash)
        mediaHash.pop(unique_id)
        if data:
            return [data,file_hash]
        return "0"

    name=str(request.form['name'])
    typ=str(request.form['typ'])
    curr=str(request.form['server'])
    chunk=request.files['chunk'].read()
    unique_id = str(uuid.uuid4())
    with open(media_dir+"/"+ unique_id ,"wb") as file:
        file.write(chunk)
    hasher=hashlib.sha256()
    hasher.update(chunk)
    mediaHash[unique_id]=[hasher,name,typ,curr]  #store name,typ,hasher in List :
    # For small files. I don't have time to reimplement this
    if request.form.get('dN'):
        file_hash=hasher.hexdigest()
        data = uploadSuccess(unique_id,file_hash)
        mediaHash.pop(unique_id)
        if data:
            return [data,file_hash]
        return "0"
    return unique_id

# Only you(valid person) should know about the file.
@app.route("/media/<srvr>/<id>",methods=["GET"])
def handel_get_Media(srvr,id):
    if srvr not in session.get("myserver"):
        return "0"
    Media=server[srvr].query(media).filter_by(id=id).first()
    if Media != None:
        file_path=media_dir+'/'+Media.hash
        if os.path.exists(file_path):
            return send_file(os.path.realpath(file_path))
        else:
            print(file_path)
            return make_response('Not found',404)
    else:
        return make_response('Not found',404)


import json, datetime, time
from .. import socketio, rooms, server, tables, india_timezone
from flask import request, session, Blueprint
from ..database.models import media, channel, users
from ..database.database_utils import create_channel
from bidict import bidict

sockets = Blueprint("sockets",__name__)


@socketio.on('setPubKey')
def handel_Pub_Key(pub_key):
    if isinstance(pub_key,str) and len(pub_key):
        mydata=rooms[request.sid]
        mydata.inverse[mydata[request.sid]]=pub_key

@socketio.on('disconnect')
def on_disconnect():
    # could just pop those values 
    socketio.server.leave_room(request.sid, room=None)
    socketio.server.leave_room(request.sid, room=request.sid)
    for srvr in session.get("myserver"):
        myserver = rooms.get(srvr)
        if myserver:
            myserver.pop(session.get(srvr),None)
            # I m doing this because I don't want to delete the bidict({}) if empty
            # socketio.server.leave_room(session.get(srvr),to=srvr)
            socketio.emit("notify",[srvr,session.get(srvr),session.get("name"),None],to=srvr) 

@socketio.on('Load')
def Load(data):
    start_time = time.time()
    srvr=data.get('server')
    if srvr in session.get('myserver'): # And wheater the reqsrvr is in server.keys()
        id=session.get(srvr)
        (pub_key,eio_sid)=next(iter(rooms[request.sid].items()))
        socketio.emit("notify",[srvr,id,session.get("name"),pub_key],to=srvr)
        rooms[srvr][id]=eio_sid
        db=server[srvr]

        serverInfo={'server':srvr,'id':id,'name':tables[srvr]["Name"]}

        channels=db.query(channel).all()   # later on we can limit this for sync sliding
        chnlCount=len(data.get("msg",0))   # I can definately use the dict which store

        serverInfo['channels']=[]          # all the channels i just need time.
        for chnl in channels:
            if chnl.id>chnlCount:
                serverInfo['channels'].append({'id':chnl.id,
                                             'name':chnl.name,
                                             'creator':chnl.user.username})

        Media=db.query(media).filter(media.id>data.get('media',0)).all()
        serverInfo['medias']=[{'id':media.id,
                               'hash':media.hash,
                               'name':media.name,
                               'permissions':media.permissions
                               } for media in Media]

        User=db.query(users).all()
        serverInfo['users']={user.id:{ 'name':user.username,
                                       'role':user.role.id
                                     } for user in User}
        peers={}
        for id,eid in rooms[srvr].items():
            sid=rooms[None].inverse.get(eid)
            (pub_key,_)=next(iter(rooms[sid].items()))
            peers.update({id:pub_key})
        serverInfo['live']=peers

        finish_time = time.time()
        total_time = finish_time-start_time
        print("to create serverInfo : "+str(total_time))
        socketio.emit("server",serverInfo,to=request.sid) # send serverInfo
        finish_time = time.time()
        total_time = finish_time-start_time
        print("to create serverInfo : "+str(total_time))

        for chnl in channels:
            start_time = time.time()
            last_msg_id=data.get('msg').get(str(chnl.id),0)
            ch=tables[srvr][chnl.id]
            last_msgs=db.query(ch).order_by(ch.id.desc()).filter(ch.id>last_msg_id).limit(30)
            Msgs=[srvr,chnl.id]
            Msgs.append([[msg.id,msg.data,msg.user.username] for msg in last_msgs])
            finish_time = time.time()
            total_time = finish_time-start_time
            print("for messages of channel : "+str(total_time))
            socketio.emit("messages",Msgs,to=request.sid)

@socketio.on("create")
def create(newchannel):
    start_time = time.time()
    curr=newchannel[0]
    name=newchannel[1]
    id=session.get(curr)
    #isCreationAllowed = server[curr].query(admin).filter_by(id=4).first()
    #if not int(isCreationAllowed.value) :
        #adminAccount = server[curr].query(admin).filter_by(id=1).first()
        #if int(adminAccount.value) != id:
        #    return
    if curr not in session.get("myserver"):
        return
    new = create_channel(curr,name,id)
    finish_time = time.time()
    total_time = finish_time-start_time
    print("to create channel : "+str(total_time))
    socketio.emit("show_this",new,to=curr)

# @socketio.on("search_text")
# def search(text):
#    curr=session.get("server")
#    user_list=server[curr].query(users).filter(users.username.like("%"+text+"%")).all()
#    Users={"users":[user.username for user in user_list]}
#    socketio.emit("show_this",Users,to=request.sid)

@socketio.on('message')
def handel_message(message):
    start_time = time.time()
    msg={}
    msgData=message.get('msgData')
    if msgData:
        msg[0]=msgData
    curr=message.get('server')
    if curr not in session.get("myserver"):
        return
    mediaId=message.get('mediaId')
    if mediaId:
        Media=server[curr].query(media).filter_by(id=mediaId).first()
        if Media==None:
            return
        print('media')
        msg[1]=mediaId
    id=session.get(curr)
    name=session.get("name")
    channel_id=int(message.get('channel'))
    msg[3]=datetime.datetime.now(india_timezone).strftime('%d-%m-%Y %H:%M:%S')
    if channel_id <= tables[curr]['Len']:
        replyId=message.get('replyId')
        if replyId:
            reply=server[curr].query(tables[curr][channel_id]).filter_by(id=int(replyId)).first()
            if reply==None:
                return
            print('reply')
            msg[2]=replyId
        Msg=json.dumps(msg)
        message=tables[curr][channel_id](data=Msg,sender_id=id)
        server[curr].add(message)
        server[curr].commit()
        finish_time = time.time()
        total_time = finish_time-start_time
        print("to send message : "+str(total_time))
        socketio.emit('show_message',[curr,channel_id,message.id,msg,name], to=curr)

# This is what E2EE looks like.
@socketio.on('chat')
def handel_chat(chat):
    start_time = time.time()
    curr=chat.get('server')
    reciever=chat.get('id')
    enc_msg=chat.get('msg')
    if curr not in session.get('myserver') or not enc_msg or not isinstance(reciever,int):
        return
    id=session.get(curr)
    resvrEID=socketio.server.manager.rooms['/'][curr].get(reciever)
    if resvrEID:
        resvrSID=socketio.server.manager.rooms['/'][None].inverse.get(resvrEID)
        finish_time = time.time()
        total_time = finish_time-start_time
        print("to send dm : "+str(total_time))
        socketio.emit('dm',[curr,id,enc_msg],to=resvrSID)

@socketio.on('reaction') # Name is enough.
def reaction(Data):
    start_time = time.time()
    curr=Data[0]
    if curr not in session.get("myserver"):
        return
    id=session.get(curr)
    channel_id=int(Data[1])
    # FOR CHANNEL
    if channel_id <= tables[curr]['Len']:
        msg=server[curr].query(tables[curr][channel_id]).filter_by(id=Data[2]).first()
        if msg:
            message=json.loads(msg.data)
            if Data[3]:
                if message.get('4'):
                    message['4'][str(id)]=Data[3]
                else:
                    message['4']={str(id):Data[3]}
            else:
                message['4'].pop(str(id))
                Data[3]=None
            data=json.dumps(message)
            msg.data=data
            server[curr].commit()
            finish_time = time.time()
            total_time = finish_time-start_time
            print("to react on message : "+str(total_time))
            socketio.emit('reaction',[curr,channel_id,msg.id,id,Data[3]],to=curr)

@socketio.on('getHistory') # Name is enough.
def getHistory(data):
    start_time = time.time()
    curr=data.get("server")
    try:
        lastMsg=int(data.get('lastMsg'))
        channelId=int(data.get('channel'))
    except:
        return
    if curr in session.get("myserver") and channelId <= tables[curr]['Len']:
        channel=tables[curr][channelId]
        last_msgs=server[curr].query(channel).order_by(channel.id.desc()).filter(channel.id<lastMsg).limit(30)
        Msgs=[[msg.user.username,msg.id,msg.data] for msg in last_msgs]
        Msgs=[curr,channelId]
        Msgs.append([[msg.id,msg.data,msg.user.username] for msg in last_msgs])
        finish_time = time.time()
        total_time = finish_time-start_time
        print("to get history : "+str(total_time))
        socketio.emit("messages",Msgs,to=request.sid)


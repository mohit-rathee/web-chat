from flask import request, session, Blueprint
from .. import socketio, rooms, server
from bidict import bidict

sockets = Blueprint("sockets",__name__)

# Manually creating spaces and rooms in socketio. coz I m A-Fish-ant.
rooms['app']=bidict({}) # Structure is lib specific.

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
            # socketio.server.leave_room(session.get(srvr),room=srvr)
            socketio.emit("notify",[srvr,session.get(srvr),session.get("name"),None],room=srvr) 

@socketio.on('Load')
def Load(data):
    reqsrvr=data.get('server')
    if reqsrvr in session.get('myserver'): # And wheater the reqsrvr is in server.keys()
        id=session.get(reqsrvr)
        (pub_key,eio_sid)=next(iter(rooms[request.sid].items()))
        socketio.emit("notify",[reqsrvr,id,session.get("name"),pub_key],room=reqsrvr)
        rooms[reqsrvr][id]=eio_sid
        serverInfo={'server':reqsrvr,'id':id}
        curr=server[reqsrvr]
        channels=curr.query(channel).all() #later on we can limit this for sync sliding
        chnlCount=len(data.get("msg",0))   # I can definately use the dict which store
        serverInfo['channels']={}          # all the channels i just need time.
        for chnl in channels:
            if chnl.id>chnlCount:
                serverInfo['channels'][chnl.id]=[chnl.id,chnl.name,chnl.user.username]
        Media=curr.query(media).filter(media.id>data.get('media',0)).all()
        serverInfo['medias']={media.id:[media.id,media.hash,media.name] for media in Media}
        User=curr.query(users).all()
        serverInfo['users']={user.id:user.username for user in User}
        Dict={}
        for id,eid in rooms[reqsrvr].items():
            sid=rooms[None].inverse.get(eid)
            (pub_key,_)=next(iter(rooms[sid].items()))
            Dict.update({id:pub_key})
        serverInfo['live']=Dict
        socketio.emit("server",serverInfo,to=request.sid)
        for chnl in channels:
            lastid=data.get('msg').get(str(chnl.id),0)
            ch=Tables[reqsrvr][chnl.id]
            last_msgs=curr.query(ch).order_by(ch.id.desc()).filter(ch.id>lastid).limit(30)
            Msgs=[reqsrvr,chnl.id]
            Msgs.append([[msg.id,msg.data,msg.user.username] for msg in last_msgs])
            socketio.emit("messages",Msgs,to=request.sid)

@socketio.on("create")
def create(newchannel):
    curr=newchannel[0]
    id=session.get(curr)
    isCreationAllowed = server[curr].query(admin).filter_by(id=4).first()
    if not int(isCreationAllowed.value) :
        adminAccount = server[curr].query(admin).filter_by(id=1).first()
        if int(adminAccount.value) != id:
            return
    if curr not in session.get("myserver"):
        return
    Topic=channel(name=newchannel[1],creator_id=id)
    server[curr].add(Topic)
    server[curr].commit()
    Base=base[curr]
    Tables[curr][Topic.id]=create_channel(Topic.id, Base,users)
    Tables[curr]["Len"]+=1
    Base.metadata.create_all(engine[curr])
    new={"channel":[curr,Topic.id,Topic.name,Topic.user.username]}
    socketio.emit("show_this",new,room=curr)

# @socketio.on("search_text")
# def search(text):
#    curr=session.get("server")
#    user_list=server[curr].query(users).filter(users.username.like("%"+text+"%")).all()
#    Users={"users":[user.username for user in user_list]}
#    socketio.emit("show_this",Users,to=request.sid)

@socketio.on('message')
def handel_message(message):
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
        msg[1]=mediaId
    id=session.get(curr)
    name=session.get("name")
    channel_id=int(message.get('channel'))
    msg[3]=datetime.datetime.now(india_timezone).strftime('%d-%m-%Y %H:%M:%S')
    if channel_id <= Tables[curr]['Len']:
        replyId=message.get('replyId')
        if replyId:
            reply=server[curr].query(Tables[curr][channel_id]).filter_by(id=int(replyId)).first()
            if reply==None:
                return
            msg[2]=replyId
        Msg=json.dumps(msg)
        message=Tables[curr][channel_id](data=Msg,sender_id=id)
        server[curr].add(message)
        server[curr].commit()
        socketio.emit('show_message',[curr,channel_id,message.id,msg,name], room = curr)

# This is what E2EE looks like.
@socketio.on('chat')
def handel_chat(chat):
    curr=chat.get('server')
    reciever=chat.get('id')
    enc_msg=chat.get('msg')
    if curr not in session.get('myserver') or not enc_msg or not isinstance(reciever,int):
        return
    id=session.get(curr)
    resvrEID=socketio.server.manager.rooms['/'][curr].get(reciever)
    if resvrEID:
        resvrSID=socketio.server.manager.rooms['/'][None].inverse.get(resvrEID)
        socketio.emit('dm',[curr,id,enc_msg],to=resvrSID)
    else:
        print('friend is offline')

@socketio.on('reaction') # Name is enough.
def reaction(Data):
    curr=Data[0]
    if curr not in session.get("myserver"):
        return
    id=session.get(curr)
    channel_id=int(Data[1])
    # FOR CHANNEL
    if channel_id <= Tables[curr]['Len']:
        msg=server[curr].query(Tables[curr][channel_id]).filter_by(id=Data[2]).first()
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
            socketio.emit('reaction',[curr,channel_id,msg.id,id,Data[3]],to=curr)

@socketio.on('getHistory') # Name is enough.
def getHistory(data):
    curr=data.get("server")
    try:
        lastMsg=int(data.get('lastMsg'))
        channelId=int(data.get('channel'))
    except:
        return
    if curr in session.get("myserver") and channelId <= Tables[curr]['Len']:
        channel=Tables[curr][channelId]
        last_msgs=server[curr].query(channel).order_by(channel.id.desc()).filter(channel.id<lastMsg).limit(30)
        Msgs=[[msg.user.username,msg.id,msg.data] for msg in last_msgs]
        Msgs=[curr,channelId]
        Msgs.append([[msg.id,msg.data,msg.user.username] for msg in last_msgs])
        socketio.emit("messages",Msgs,to=request.sid)


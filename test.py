import hashlib
import asyncio
async def updateHash():
    hasher=hashlib.sha256()
    while True:
        arg = yield hasher.hexdigest()
        await asyncio.sleep(3)
        print((hasher.hexdigest() + arg).encode())
        hasher.update((hasher.hexdigest() + arg).encode())
async def wait(s):
    await asyncio.sleep(s)
    return "took "+str(s)+" sec" 
async def main():
    hash_generator = updateHash()
    await hash_generator.asend(None)
    result1 = await asyncio.gather(wait(1),hash_generator.asend("arg1"))
    print(result1)
    result2 = await asyncio.gather(hash_generator.asend("arg2"),wait(2))
    print(result2)  
    result3 = h
    print(result3)
asyncio.run(main())

def createNewDatabase(BASE,name):
    print(base)
    attrs = {
        '__tablename__':'users',
        'id': Column(db.Integer, primary_key=True),
        'username': Column(db.String, unique=True, nullable=False),
        'password': Column(db.String(77), nullable=False),
    }
    users = type('users', (Base,), attrs)
    Tables[name]["users"]=users
    print(Tables[name]["users"])
    attrs = {
        '__tablename__':'channel',
        'id': Column(db.Integer, primary_key=True),
        'name': Column(db.String, nullable=False),
        'creator_id': Column(db.Integer, db.ForeignKey(Tables[name]["users"].id)),
        'user': db.relationship(Tables[name]["users"])
    }
    channel = type('channel', (Base,), attrs)
    Tables[name]["channel"]=channel
    print(Tables[name]["channel"])
    attrs = {
        '__tablename__':'chats',
        'id': Column(db.Integer, primary_key=True),
        'key': Column(db.String, nullable=False),
        'data': Column(JSON, nullable=False),
    }
    chats = type('chats', (base,), attrs)
    Tables[name]["chats"]=chats
    print(Tables[name]["chats"])
    attrs = {
        '__tablename__':'media',
        'id': Column(db.Integer, primary_key=True),
        'data': Column(JSON, nullable=False),
    }
    media = type('media', (Base,), attrs)
    Tables[name]["media"]=media
    print(Tables[name]["media"])

    Base.metadata.create_all(bind=Engine)
    base[name]=Base

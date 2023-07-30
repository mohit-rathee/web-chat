# web-chat
 https://web-chat.onrender.com
 
- A full-fledged lightweight chatting website [web-chat](https://web-chat.onrender.com) 
- Integrated with [web-sockets](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API) for live updates of users.
- It is a discord clone where you can create/add a new server.*Basically databases
- You can send, react and reply messages (super efficient)
- web-chat never saves your data it just take a file update it when you use web-chat and then it is available for you to download/save to yourside.
- Multiple Servers can coexist without any interference.
- You can chose which server you wanna join (at registration).
- No choise would be needed at login. It automatically tracks your account and give you access to all registered accounts
- You can share media files too and forward them without increasing storage

## Stack Used:
I used flask with sqlachemy,postgress and gunicorn for websockets and some html ,css ,javascript.

## Future Ideas.
- Use indexedDB to store chats for quick response.
- Add a feature to create a profile/description to every Server, Channel, User. Just an md file like github.
- Streaming media files to client more fastly.
- Add a personal encryption & decryption protocol.
  
## Installation for linux :
1. Clone this repo.
2. Then open folder and create a virtual environment `python3 -m venv venv`
3. Run `. venv/bin/activate`
4. Install the essential things `pip install -r requirement.txt`
5. Either run `export DATABASE_URI=sqlite:///<path_to_store_database>test.sqlite3` and `export SECRET_KEY=<a_secret_key>` or edit the app.py file manually
6. Start the service by cmd `gunicorn --worker-class geventwebsocket.gunicorn.workers.GeventWebSocketWorker app:app`  
   (change the default url in app.py if you want to).

# To Approach:
- My mail : mohit.rathee2505@gmail.com

## For developers:
Your are free to add/change the feature according to your will but don't forget to show me your creation.

# web-chat
 https://web-chat.onrender.com
 
- A full-fledged lightweight chatting website [web-chat](https://web-chat.onrender.com) 
- Integrated with [web-sockets](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API) and live updates of other users.
- It is a discord clone where you can create/add a new server.*Basically databases
- web-chat never saves your data it just take a file update it when you use web-chat and then it is available for you to download/save to yourside.
- Multiple Servers can coexist without any interference.
- You can chosse which server you wanna join at signup.
- No choise would be needed at login. It automatically tracks your account and give you access to all registered accounts

## Stack Used:
I used flask with sqlachemy and gunicorn for websockets and some html ,css ,javascript.

## Future Ideas.
- Wanna add group chat via webrtc.
- use local storage to store chats and automatic cleanup's at logout.
- Add a feature to create a profile to every Server, Channel, User. Just an md file like github.


## Installation for linux :
1. Clone this repo.
2. Then open folder and create a virtual environment `python3 -m venv venv`
3. Run `. venv/bin/activate`
4. Install the essential things `pip install -r requirement.txt`
5. Start the service by cmd `gunicorn --worker-class geventwebsocket.gunicorn.workers.GeventWebSocketWorker app:app`  
   (change the default url in app.py if you want to).

# To Approach:
- My mail : mohit.rathee2505@gmail.com

## For developers:
Your are free to add/change the feature according to your will but don't forget to show me your creation.

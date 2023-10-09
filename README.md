# web-chat
A lightweight web based chatting application [web-chat](https://web-chat.onrender.com) .
![image](https://github.com/mohit-rathee/web-chat/assets/89066152/fd9a022e-487f-4e9b-8170-276bee282808)

 ## Features
- Integrated with [web-sockets](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API) for live updates of users.
- Just like discord, you can create your own server or join others server.
- You can have channels over which you can communicate with other members.
- We allow you to remove your server from web-chat and download the state of server locally.
- You can upload it later and resume your state.
- There can be multiple servers on web-chat you can access.
- You can share media files on server which is available to all members of the server.
- Your messages/media are cached on your device for quick and offline access.[[IndexedDB](https://developer.mozilla.org/en-US/docs/Web/API/IndexedDB_API)]

## Future Ideas.
- Add some features for customising server.
- Add a feature to create a description to things.
- Use some frontend framework someday.
- Add a personal encryption & decryption protocol at p2p level.
  
## Running locally on linux:
1. Clone this repo.
2. Then open folder and create a virtual environment `python3 -m venv venv`
3. Run `. venv/bin/activate`
4. Install the essential things `pip install -r requirement.txt`
5. Run `export DATABASE_URI=sqlite:///test.sqlite3` and `export SECRET_KEY=<a_secret_key>`.
6. Start the service by cmd `gunicorn --worker-class geventwebsocket.gunicorn.workers.GeventWebSocketWorker app:app`  

# To Approach:
- My mail : mohit.rathee2505@gmail.com

## For developers:
Your are free to add/change the feature according to your will but don't forget to show me your creation.

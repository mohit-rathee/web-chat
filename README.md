# Web-Chat 🚀

A lightweight web-based chatting application that brings real-time communication to your fingertips. Join the conversation at [web-chat](https://web-chat.onrender.com).

![Web-Chat](https://github.com/mohit-rathee/web-chat/assets/89066152/fd9a022e-487f-4e9b-8170-276bee282808)

## Features
- **Real-Time Updates:** Powered by [WebSockets](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API) for live user interaction.
- **Create or Join Servers:** Just like Discord, you can create your own server or join existing ones.
- **Channel Communication:** Organize your conversations with channels for seamless communication.
- **Server State Management:** Download and save your server's state locally, making it easy to resume later.
- **Multi-Server Access:** Connect to multiple servers on Web-Chat for diverse conversations.
- **Media Sharing:** Share media files with all server members for a richer chat experience.
- **Local Caching:** Your messages and media are cached on your device for quick and offline access using [IndexedDB](https://developer.mozilla.org/en-US/docs/Web/API/IndexedDB_API).

## Future Ideas
- **Custom Server Features:** Allow users to customize their servers to their liking.
- **Descriptions:** Add the ability to include descriptions to your server or content.
- **Frontend Framework:** Consider incorporating a frontend framework to enhance the user interface.
- **Private Messaging(Comming Soon):** Messages will be stored only on your device, ensuring the utmost privacy.
- **Security:**  Private messaging feature with robust end-to-end encryption (on p2p level).

## Running Locally on Linux
1. Clone this repository.
2. Navigate to the folder and create a virtual environment: `python3 -m venv venv`
3. Activate the virtual environment: `. venv/bin/activate`
4. Install the necessary dependencies: `pip install -r requirements.txt`
5. Set up environment variables: 
   - `export DATABASE_URI=sqlite:///test.sqlite3`
   - `export SECRET_KEY=<a_secret_key>`
6. Start the service with Gunicorn: `gunicorn --worker-class geventwebsocket.gunicorn.workers.GeventWebSocketWorker app:app`

## How to Reach Me
- 📧 Email: mohit.rathee2505@gmail.com

## For Developers
Feel free to contribute, add, or modify features according to your creative ideas. Don't forget to share your creations with me!

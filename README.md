# web-chat
 https://web-chat.onrender.com
 
Here i created a kind of experimental state of an online chat application. It do not use sockets which means none other user will get notified when you send text(until now).It saves data of your session in server usually and allow you to download that as a file(***.db).Now just upload that file ,and continue from where you left. 
(this is because your data might not be saved for long time where i hosted this app).You can use this project in your local area network instead of using emails and messages which rely on the network outside the network i.e. Internet


## Installation for linux local machine:
1. Clone this repo.
2. Then open folder and create a virtual environment `python3 -m venv venv`
3. Run `. venv/bin/activate`
4. Install the essential things `pip install -r requirement.txt`
5. Start the service by cmd `flask run`.(if you known flask then you can change the default url)


## Installation for Windows local machine:
1. Clone this repo.
2. Then open folder and create a virtual environment by cmd `py -3 -m venv venv`
3. Run `venv\Scripts\activate`
4. Install the essential things `pip install -r requirement.txt`
5. Start the service by cmd `flask run`.(if you known flask then you can change the default url)

## For developers:
Your are free to add/change the feature according to your will but don't forget to show me your creation.
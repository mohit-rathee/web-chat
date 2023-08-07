// // Step 1: Open a connection to the IndexedDB database
// const chatMessages = [
//   {
//     roomId: 1,
//     messageId: 1,
//     sender: 1,
//     text: "Hello, this is room 1.",
//   },
//   { roomId: 1, messageId: 2, sender: 2, text: "Nice to meet you!" },
//   {
//     roomId: 2,
//     messageId: 1,
//     sender: 1,
//     text: "Welcome to room 2.",
//   },
//   // More messages for different chat rooms...
// ];
function createDatabase(name, version) {
  return new Promise((resolve, reject) => {
    let present = true;
    const request = indexedDB.open(name, version);

    request.onupgradeneeded = function (event) {
      const db = event.target.result;
      db.createObjectStore("channels", { keyPath: "cid" });
      db.createObjectStore("users", { keyPath: "uid" });
      const mediaStore = db.createObjectStore("medias", { keyPath: "mdid" });
      const chatStore = db.createObjectStore("messages", {
        keyPath: ["rid", "mid"],
      });
      chatStore.createIndex("by_rid", "rid");
      present = false;
    };

    request.onsuccess = function (event) {
      const db = event.target.result;
      console.log("Database connection established.");
      resolve([db, present]);
    };

    request.onerror = function (event) {
      console.error("Error opening database:", event.target.errorCode);
      reject(event.target.errorCode);
    };
  });
}
const DBs = {};
socket.on("connect", function () {
  myservers.forEach((srvr) => {
    console.log(srvr)
    createDatabase(srvr,1).then((db) => {
      if (db[1] == true) {
        console.log("database was present");
        socket.emit("Load",srvr)
      } else {
        console.log("database was not present");
        socket.emit("Load",srvr);
      }
      DBs[srvr] = db[0];
      console.log(DBs);
    });
  });
});

socket.on("messages",function(messages){
  console.log(messages)
  const db=DBs[messages[0]]
  const roomId = messages[1]
  if(db){
    const trxn = db.transaction("messages","readwrite")
    const messagesStore = trxn.objectStore("messages");
    messages[2].forEach((msg)=>{
      const mssg={"rid":roomId,"mid":msg[0],"data":JSON.parse(msg[1]),"sender":msg[2]}
      console.log(mssg)
      messagesStore.put(mssg)
    })
    trxn.oncomplete = function () {
      console.log("Messages of "+roomId+" added to the messages object store.");
    };
  }
})

socket.on("server", function (data) {
  console.log(data);
  addserver(data[0]);
  const db = DBs[data[0]]
  localStorage.setItem("server", data[0]);
  if(db){
    serverList[data[0]]=data[1]
    const trxn= db.transaction(["channels","users","medias"],"readwrite")
    const channelStore = trxn.objectStore("channels");
    data[1].forEach((ch) => {
      const chnl = {"cid":ch[0],"name":ch[1],"creator":ch[2]}
      channelStore.put(chnl)
      if (curr) {
        server.innerText = data[0]; //this is not efficient
        showing(ch);
      }
    });
    const mediaStore = trxn.objectStore("medias")
    data[2].forEach((md) => {
      const name = JSON.parse(md[2]);
      md[2] = name;
      const media = {"mdid":md[0],"hash":md[1],"name":name[0],"mime":name[1]}
      mediaStore.put(media)
      if (curr) {
        addmedia(md);
      }
    });
    mediaList[data[0]] = data[2];
    const userStore = trxn.objectStore("users")
    data[3].forEach((usr)=>{
      const user = {"uid":usr[0],"name":usr[1]}
      userStore.put(user)
    })    
    curr = false;
  }
});

function store_in_db() {
  const transaction = DBs.app.transaction("messages", "readwrite");
  const chatStore = transaction.objectStore("messages");
  chatMessages.forEach((msg) => {
    chatStore.put(msg);
  });
  transaction.oncomplete = function () {
    console.log("Messages added to the chat_messages object store.");
  };
}
function get_from_db() {
  const transaction = DBs.app.transaction("messages", "readwrite");
  const chatStore = transaction.objectStore("messages");
  const roomIndex = chatStore.index("by_roomId");
  const req = roomIndex.getAll(IDBKeyRange.only(1));
  req.onsuccess = function (event) {
    const chatMessages = event.target.result;
    console.log("All messages:", chatMessages);
  };
}

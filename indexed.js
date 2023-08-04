// Step 1: Open a connection to the IndexedDB database
const chatMessages = [
  {
    roomId: 1,
    messageId: 1,
    sender: 1,
    text: "Hello, this is room 1.",
  },
  { roomId: 1, messageId: 2, sender: 2, text: "Nice to meet you!" },
  {
    roomId: 2,
    messageId: 1,
    sender: 1,
    text: "Welcome to room 2.",
  },
  // More messages for different chat rooms...
];
function createDatabase(name, version) {
  return new Promise((resolve, reject) => {
    let present = true;
    const request = indexedDB.open(name, version);

    request.onupgradeneeded = function (event) {
      const db = event.target.result;
      db.createObjectStore("channels", { keyPath: "channelId" });
      db.createObjectStore("users", { keyPath: "userId" });
      db.createObjectStore("medias", { keyPath: "mediaId" });
      const chatStore = db.createObjectStore("messages", {
        keyPath: ["roomId", "messageId"],
      });
      chatStore.createIndex("by_roomId", "roomId");
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
createDatabase("app", 1).then((db) => {
  if (db[1] == true) {
    console.log("database was present");
    // const checklist = getchecklist(db[0])
  } else {
    console.log("database was not present");
    // socket.emit(Load,false)
  }
  DBs["app"] = db[0];
  console.log(DBs);
  store_in_db()
  get_from_db()
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

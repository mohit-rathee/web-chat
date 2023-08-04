const db = createDatabase("app", 1);

function createDatabase(name, version) {
  const request = indexedDB.open(name, version);

  request.onupgradeneeded = function (event) {
    const db = event.target.result;
    //   db.createObjectStore("server")
    db.createObjectStore("channels", { keyPath: "channelId" });
    db.createObjectStore("users", { keyPath: "userId" });
    db.createObjectStore("medias", { keyPath: "mediaId" });
    const chatStore = db.createObjectStore("messages", {
      keyPath: ["roomId", "messageId"],
    });
    chatStore.createIndex("by_roomId", "by_messageId");
  };

  request.onsuccess = function (event) {
    const db = event.target.result;
    console.log("Database connection established.");
    return db;
  };

  request.onerror = function (event) {
    console.error("Error opening database:", event.target.errorCode);
    return 0
  };
}

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
      db.createObjectStore("medias", { keyPath: "mdid" });
      const chatStore = db.createObjectStore("messages", {
        keyPath: ["rid", "mid"],
      });
      chatStore.createIndex("by_rid", "rid");
      present = false;
    };

    request.onsuccess = function (event) {
      const db = event.target.result;
      // console.log("Database connection established.");
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
  servers.innerHTML = "";
  myservers.forEach((srvr) => {
    createDatabase(srvr, 1).then((db) => {
      if (db[1] == true) {
        // console.log("database was present");
        socket.emit("Load", srvr);
      } else {
        // console.log("database was not present");
        socket.emit("Load", srvr);
      }
      DBs[srvr] = db[0];
    });
  });
});
socket.on("server", function (data) {
  addserver(data[0]);
  const db = DBs[data[0]];
  let bool = false;
  if (!localStorage.getItem("server")) {
    localStorage.setItem("server", data[0]);
    bool = true;
  }
  if (db) {
    const trxn = db.transaction(["channels", "users", "medias"], "readwrite");
    const channelStore = trxn.objectStore("channels");
    data[1].forEach((ch) => {
      const chnl = { cid: ch[0], name: ch[1], creator: ch[2] };
      channelStore.put(chnl);
      if (bool) {
        server.innerText = data[0]; //this is not efficient
        showing(chnl, false);
      }
    });
    const mediaStore = trxn.objectStore("medias");
    data[2].forEach((md) => {
      const name = JSON.parse(md[2]);
      const media = { mdid: md[0], hash: md[1], name: name[0], mime: name[1] };
      mediaStore.put(media);
      if (bool) {
        addmedia(media);
      }
    });
    const userStore = trxn.objectStore("users");
    // userCount.innerText = Object.keys(data[4]).length;//later length is send by server
    if (bool) {
      userCount.innerText = 0;
    }
    for (let key in data[4]) {
      const user = { uid: Number(key), name: data[3][key], sid: data[4][key] };
      userStore.put(user);
      if (bool) {
        showUser(data[3][key]);
      }
      delete data[3][key];
    }
    for (let key in data[3]) {
      const user = { uid: Number(key), name: data[3][key], sid: null };
      userStore.put(user);
    }
  }
});

socket.on("notify", function (data) {
  const db = DBs[data[0]];
  const trxn = db.transaction("users", "readwrite");
  const userStore = trxn.objectStore("users");
  const user = { uid: data[1], name: data[2], sid: data[3] };
  userStore.put(user);
  if (data[0] == localStorage.getItem("server")) {
    if (data[3]) {
      showUser(data[2]);
    } else {
      removeUser(data[2]);
    }
  }
});
function showUser(name) {
  if (!document.getElementsByClassName('U-'+name).length){
    userCount.innerText = parseInt(userCount.innerText) + 1;
    const user = document.createElement("li");
    user.classList.add("U-" + name);
    user.innerText = name;
    user.setAttribute("onclick", 'GOTOfrnd("' + name + '")');
    userList.appendChild(user);
  }
}
function removeUser(name) {
  const user = document.getElementsByClassName("U-" + name)[0];
  if (user) {
    userCount.innerText = parseInt(userCount.innerText) - 1;
    user.remove();
  }
}
function getChannels(server) {
  const transaction = DBs[server].transaction("channels", "readonly");
  const channels = transaction.objectStore("channels");
  const req = channels.getAll();
  req.onsuccess = function (event) {
    const chnls = event.target.result;
    chnls.forEach((chnl) => {
      showing(chnl, false);
    });
  };
}
function getMedia(server) {
  const transaction = DBs[server].transaction("medias", "readonly");
  const mediaStore = transaction.objectStore("medias");
  const req = mediaStore.getAll();
  req.onsuccess = function (event) {
    const media = event.target.result;
    media.forEach((md) => {
      addmedia(md);
    });
  };
}
function getPeople(server) {
  const transaction = DBs[server].transaction("users", "readonly");
  const userStore = transaction.objectStore("users");
  const req = userStore.getAll();
  req.onsuccess = function (event) {
    const users = event.target.result;
    users.forEach((user) => {
      // you can show all live + some offline users to populate the list
      if (user.sid) {
        showUser(user.name);
      }
    });
  };
}
function getMessages(server, channel) {
  const transaction = DBs[server].transaction(
    ["users", "messages"],
    "readonly"
  );
  const chatStore = transaction.objectStore("messages");
  const roomIndex = chatStore.index("by_rid");
  const req = roomIndex.getAll(IDBKeyRange.only(Number(channel)));
  req.onsuccess = async function (event) {
    const Msgs = event.target.result;
    if (Msgs.length >= 30) {
      Top.style.visibility = "visible";
    } else {
      Top.style.visibility = "hidden";
    }
    for (var i = Msgs.length - 1; i > -1; i--) {
      let reply = Number(Msgs[i].data[2]);
      if (reply) {
        //TODO: first check if reply exist in Msgs
        const repreq = chatStore.get([Number(channel), reply]);
        reply = await new Promise((resolve) => {
          repreq.onsuccess = function (event) {
            resolve(event.target.result);
          };
          repreq.onerror = function () {
            resolve(0);
          };
        });
      }
      if (Msgs[i].sender == name) {
        chatbox.insertAdjacentElement(
          "afterbegin",
          makeMessage(Msgs[i].mid, Msgs[i].data, true, reply)
        );
      } else {
        chatbox.insertAdjacentElement(
          "afterbegin",
          makeMessage(Msgs[i].mid, Msgs[i].data, false, reply)
        );
        if (i == 0 || Msgs[i].sender != Msgs[i - 1].sender) {
          chatbox.insertAdjacentElement("afterbegin", makeFrnd(Msgs[i].sender));
        }
      }
    }
    box.scrollTop = box.scrollHeight;
  };
}
socket.on("messages", function (messages) {
  const db = DBs[messages[0]];
  const roomId = messages[1];
  if (db) {
    const trxn = db.transaction("messages", "readwrite");
    const messagesStore = trxn.objectStore("messages");
    messages[2].forEach((msg) => {
      const mssg = {
        rid: roomId,
        mid: msg[0],
        data: JSON.parse(msg[1]),
        sender: msg[2],
      };
      messagesStore.put(mssg);
    });
  }
});
socket.on("media", function (data) {
  const db = DBs[data[0]];
  if (db) {
    const trxn = db.transaction(["medias"], "readwrite");
    const mediaStore = trxn.objectStore("medias");
    const media = { mdid:data[1] , hash:data[2] , name:data[3][0] , mime:data[3][1]};
    mediaStore.put(media);
    if (data[0]==localStorage.getItem("server")){
      addmedia(media);
    }else{
      shownotification('s-'+data[0])
    }
  }
});
socket.on("show_message", async function (data) {
  // TO ADD NEW CHILD OF MESSAGE //
  const db = DBs[data[0]];
  const roomId = data[1];
  const trxn = db.transaction("messages", "readwrite");
  const messagesStore = trxn.objectStore("messages");
  const msg = { rid: roomId, mid: data[2], data: data[3], sender: data[4] };
  messagesStore.put(msg);
  if (data[0] == localStorage.getItem("server")) {
    const ch = document.getElementsByClassName("c-" + String(data[1]))[0];
    if (ch.firstChild.classList.contains("active")) {
      let reply = data[3][2];
      if (reply) {
        //TODO: first check if reply exist in Msgs
        const repreq = messagesStore.get([roomId, Number(reply)]);
        reply = await new Promise((resolve) => {
          repreq.onsuccess = function (event) {
            resolve(event.target.result);
          };
          repreq.onerror = function () {
            resolve(0);
          };
        });
      }
      if (msg.sender == name) {
        chatbox.appendChild(makeMessage(msg.mid, msg.data, true,reply));
      } else {
        const allmsg = document.getElementsByClassName("frnd");
        if (allmsg[allmsg.length - 1].innerText!=msg.sender) {
          chatbox.appendChild(makeFrnd(msg.sender));
        }
        chatbox.appendChild(makeMessage(msg.mid, msg.data, false,reply));
      }
      box.scrollTop = box.scrollHeight;
    } else {
      shownotification("c-", data[1]);
    }
  } else {
    shownotification("s-", data[0]);
  }
});
socket.on("reaction", function (reactData) {
  const db = DBs[reactData[0]];
  const roomId = reactData[1];
  const messageId = reactData[2];
  const trxn = db.transaction("messages", "readwrite");
  const messagesStore = trxn.objectStore("messages");
  const req = messagesStore.get([roomId, messageId]);
  req.onsuccess = function (event) {
    const msg = event.target.result;
    const message = msg.data;
    if (message[4]) {
      if (reactData[4]) {
        message[4][reactData[3]] = reactData[4];
      } else {
        delete message[4][reactData[3]];
        if (!message[4].length) {
          delete message[4];
        }
      }
    } else {
      message[4] = {};
      message[4][reactData[3]] = reactData[4];
    }
    messagesStore.put(msg);
    if (reactData[0] == localStorage.getItem("server")) {
      if (reactData[1] == localStorage.getItem("channel")) {
        const myreaction = document.getElementsByClassName(
          "m-" + reactData[2] + "r-" + reactData[3]
        );
        if (myreaction.length) {
          myreaction[0].innerText = reactData[4];
        } else {
          const reaction = document.getElementsByClassName(
            "r-" + reactData[2]
          );
          if (reaction.length) {
            const EMOG = document.createElement("div");
            EMOG.classList.add("m-" + reactData[2] + "r-" + reactData[3]);
            EMOG.innerText = reactData[4];
            EMOG.classList.add("react");
            if (reactData[3] == userid) {
              EMOG.classList.add("myreaction");
            }
            reaction[0].appendChild(EMOG);
          } else {
            const Message = document.getElementsByClassName(
              "m-" + reactData[2]
            );
            if (Message.length) {
              const reactionpallet = document.createElement("div");
              reactionpallet.classList.add("reactions");
              reactionpallet.classList.add("r-" + reactData[2]);
              const EMOG = document.createElement("div");
              EMOG.classList.add("m-" + reactData[2] + "r-" + reactData[3]);
              EMOG.innerText = reactData[4];
              EMOG.classList.add("react");
              if (reactData[3] == userid) {
                EMOG.classList.add("myreaction");
              }
              reactionpallet.appendChild(EMOG);
              Message[0].appendChild(reactionpallet);
            }
          }
        }
      }else{
        shownotification('c-',String(reactData[1]))
      }
    }else{shownotification('s-',reactData[0])}
  };
});

function makeMessage(id, msg, bool, reply = null) {
  const message = document.createElement("div");
  message.classList.add("message");
  const msgPara = document.createElement("p");
  msgPara.classList.add("m-" + id);
  const more = document.createElement("div");
  more.classList.add("moremenu");
  more.setAttribute(
    "onclick",
    "showmoremenu(this.parentElement.parentElement)"
  );
  msgPara.appendChild(more);
  if (reply) {
    const replyof = document.createElement("div");
    const repid = msg[2];
    if (reply != 0) {
      const sender = reply.sender;
      const repmsg = reply.data[0];
      if (!repmsg) {
        repmsg = "";
      }
      replyof.innerText = sender + ": " + repmsg;
      if (reply.data[1]) {
        replyof.innerText += "\n media";
      }
      replyof.setAttribute("onclick", "Focus(" + repid + ")");
    } else {
      replyof.innerText = "please go back";
    }
    replyof.classList.add("reply");
    msgPara.appendChild(replyof);
  }
  if (msg[1]) {
    // const m = mediaList[msg[1]];
    const m = document.getElementsByClassName("M-" + msg[1])[0];
    if (m) {
      // const mediatitle = document.createElement("div");
      // const nameplate = document.createElement("div");
      // nameplate.classList.add("pinned");
      // nameplate.classList.add("msg");   add this
      // const medianame = m[1][0];
      // //const hash = m[0];
      // nameplate.innerText = medianame;
      // nameplate.setAttribute("onclick", "showpinned(" + msg[1] + ")");
      // mediatitle.appendChild(nameplate);
      // // const forward=document.createElement('div')
      // // forward.classList.add('forward')
      // // forward.setAttribute(
      // //   "onclick",
      // //   'reply("' + medianame + '","' + msg[1] + '")'
      // // );
      // // mediatitle.appendChild(forward)
      // mediatitle.classList.add("mediatitle");
      const clonedparent = m.cloneNode();
      const clonedchild = m.firstChild.cloneNode(true);
      clonedchild.classList.add("msg");
      clonedparent.appendChild(clonedchild);
      msgPara.appendChild(clonedparent);
    }
  }
  if (msg[0]) {
    var text = document.createElement("div");
    text.innerText = msg[0];
    msgPara.appendChild(text);
  }
  var time = document.createElement("span");
  time.innerText = msg[3];
  msgPara.appendChild(time);
  message.appendChild(msgPara);
  const block = document.createElement("div");
  block.classList.add("menu");
  block.setAttribute("onclick", "showreactions(this.parentElement)");
  message.appendChild(block);
  message.addEventListener("mouseenter", function () {
    if (message.childElementCount == 2) {
      setTimeout(() => {
        more.style.display = "block";
        block.style.display = "block";
      }, 150);
    }
  });
  message.addEventListener("mouseleave", function () {
    if (message.childElementCount == 2) {
      setTimeout(() => {
        more.style.display = "none";
        block.style.display = "none";
      }, 150);
    }
  });
  if (bool) {
    message.classList.add("my_message");
  } else {
    message.classList.add("frnd_message");
  }
  if (msg[4] && Object.keys(msg[4]) != 0) {
    const reaction = document.createElement("div");
    reaction.classList.add("reactions");
    reaction.classList.add("r-" + id);
    Object.keys(msg[4]).forEach((k) => {
      const EMOG = document.createElement("div");
      EMOG.innerText = msg[4][k];
      EMOG.classList.add("m-" + id + "r-" + k);
      EMOG.classList.add("react");
      if (k == userid) {
        EMOG.classList.add("myreaction");
      }
      reaction.appendChild(EMOG);
    });
    reaction.classList.add("reactions");
    message.firstChild.appendChild(reaction);
  }
  return message;
}

const DBs = {};
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
      resolve([db, present]);
    };

    request.onerror = function (event) {
      console.error("Error opening database:", event.target.errorCode);
      reject(event.target.errorCode);
    };
  });
}
function getlastmsg(trxn) {
  return new Promise((resolve) => {
    const channelStore = trxn.objectStore("channels");
    const messageStore = trxn.objectStore("messages");
    const roomId = messageStore.index("by_rid");
    const messages = {}; // Store the channel ID and last message ID here
    const channelRequest = channelStore.getAll();
    channelRequest.onsuccess = function (event) {
      const channels = event.target.result;
      if (!channels) {
        resolve(messages);
      } else {
        const promises = channels.map((chnl) => {
          return new Promise((resolve, reject) => {
            const range = IDBKeyRange.only(chnl.cid);
            const messageCursorRequest = roomId.openCursor(range, "prev");
            messageCursorRequest.onsuccess = function (event) {
              const messageCursor = event.target.result;
              if (messageCursor) {
                const lastMessage = messageCursor.value;
                messages[chnl.cid] = lastMessage.mid;
                resolve();
              } else {
                messages[chnl.cid] = 0;
                resolve();
              }
            };
          });
        });
        Promise.all(promises).then(() => {
          resolve(messages);
        });
      }
    };
  });
}
function getlastmedia(trxn) {
  return new Promise((resolve) => {
    const mediaStore = trxn.objectStore("medias");
    const mediaRequest = mediaStore.openCursor(null, "prev");
    mediaRequest.onsuccess = function (event) {
      const lastMedia = event.target.result;
      if (lastMedia != null) {
        resolve(lastMedia.mdid);
      } else {
        resolve(0);
      }
    };
  });
}
function getlastuser(trxn) {
  return new Promise((resolve) => {
    const userStore = trxn.objectStore("users");
    const userRequest = userStore.openCursor(null, "prev");
    userRequest.onsuccess = function (event) {
      const lastUser = event.target.result;
      if (lastUser) {
        resolve(lastUser.uid);
      } else {
        resolve(0);
      }
    };
  });
}
async function getStatus(srvr) {
  console.log("getting status for " + srvr);
  const db = DBs[srvr];
  const status = { server: srvr };
  const trxn = db.transaction(
    ["channels", "messages", "users", "medias"],
    "readonly"
  );
  const messages = await getlastmsg(trxn);
  const lastmedia = await getlastmedia(trxn);
  const lastuser = await getlastuser(trxn);
  status["msg"] = messages;
  status["media"] = lastmedia;
  status["user"] = lastuser;
  return status;
}
async function populateRequests() {
  return new Promise(async (resolve) => {
    servers.innerHTML = "";
    const requests = [];
    const myservers = populateServer();
    const promises = myservers.map(async (srvr) => {
      const db = await createDatabase(srvr, 1);
      DBs[srvr] = db[0];
      if (db[1] == true) {
        addserver(srvr);
        if (localStorage.getItem("server")) {
          if (srvr == localStorage.getItem("server")) {
            gotoserver(srvr);
          }
        } else {
          gotoserver(srvr);
        }
        const status = await getStatus(srvr);
        requests.push(status);
      } else {
        requests.push({ server: srvr, msg: {}, media: 0, user: 0 });
      }
    });
    await Promise.all(promises);
    resolve(requests)
})}
socket.on("connect", async function () {
  const requests = await populateRequests();
  requests.forEach((srvr) => {
    console.log("sending " + srvr.server + " status to server");
    socket.emit("Load", srvr);
  });
});
socket.on("server", function (data) {
  const srvr = data.server;
  console.log(srvr + " is now up-to-date!!!");
  addserver(srvr);
  localStorage.setItem(srvr + "id", data.id);
  const db = DBs[srvr];
  let bool = false;
  if (!localStorage.getItem("server")) {
    localStorage.setItem("server", srvr);
    bool = true;
  } else {
    if (localStorage.getItem("server") == srvr) {
      bool = true;
    }
  }
  if (!db) {
    return;
  }
  const trxn = db.transaction(["channels", "users", "medias"], "readwrite");
  const channelStore = trxn.objectStore("channels");
  const channels = data.channels;

  for (const key in channels) {
    const ch = channels[key];
    const chnl = { cid: ch[0], name: ch[1], creator: ch[2] };
    channelStore.put(chnl);
    if (bool) {
      server.innerText = srvr; //this is not efficient
      showing(chnl, false);
    }
  }
  const mediaStore = trxn.objectStore("medias");
  const medias = data["medias"];
  for (const key in medias) {
    const md=medias[key]
    const name = JSON.parse(md[2]);
    const media = { mdid: md[0], hash: md[1], name: name[0], mime: name[1] };
    mediaStore.put(media);
    if (bool) {
      addmedia(media);
    }
  }
  const userStore = trxn.objectStore("users");
  // userCount.innerText = Object.keys(data[4]).length;//later length is send by server
  // if (bool) {
  //   werText = 0;
  //   userList.innerHTML=""
  // }
  const live = data.live;
  const users = data.users;
  for (let key in live) {
    const user = { uid: Number(key), name: users[key], sid: live[key] };
    userStore.put(user);
    if (bool) {
      showUser(users[key]);
    }
    delete users[key];
  }
  for (let key in users) {
    const user = { uid: Number(key), name: users[key], sid: null };
    userStore.put(user);
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
    const media = {
      mdid: data[1],
      hash: data[2],
      name: data[3][0],
      mime: data[3][1],
    };
    mediaStore.put(media);
    if (data[0] == localStorage.getItem("server")) {
      addmedia(media);
    } else {
      shownotification("s-" + data[0]);
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
        chatbox.appendChild(makeMessage(msg.mid, msg.data, true, reply));
      } else {
        const allmsg = document.getElementsByClassName("frnd");
        if (allmsg[allmsg.length - 1].innerText != msg.sender) {
          chatbox.appendChild(makeFrnd(msg.sender));
        }
        chatbox.appendChild(makeMessage(msg.mid, msg.data, false, reply));
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
  const userid = localStorage.getItem(reactData[0] + "id");
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
          const reaction = document.getElementsByClassName("r-" + reactData[2]);
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
      } else {
        shownotification("c-", String(reactData[1]));
      }
    } else {
      shownotification("s-", reactData[0]);
    }
  };
});
socket.on("show_this", function (data) {
  // if (data.hasOwnProperty("users")) {
  // data["users"].forEach((user) => {
  // GOTOfrnd(user, false);
  // });
  // } else {
  const ch = data["channel"];
  const trxn = DBs[ch[0]].transaction("channels", "readwrite");
  const channelStore = trxn.objectStore("channels");
  const chnl = { cid: ch[1], name: ch[2], creator: ch[3] };
  channelStore.put(chnl);
  showing(chnl, true);
  // }
});
// socket.on("dm", function (data) {
//   GOTOfrnd(data, (GOTO = false));
//   shownotification("f-", data);
// });
// socket.on("celebrate", function (data) {
//   console.log("hurrah");
// });

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
    const userid = localStorage.getItem(localStorage.getItem("server") + "id");
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

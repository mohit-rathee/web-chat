var socket = io({
  transports: ["websocket"],
});
const body = document.getElementById("container");
const chatbox = document.getElementById("chats");
const server = document.getElementById("server");
const line = document.getElementById("breaker");
const channel_list = document.getElementById("channel_list");
const message_form = document.getElementById("chatinput");
const message_input = document.getElementById("text_message");
const search_form = document.getElementById("search_form");
const search_input = document.getElementById("search_input");
const userlive = document.getElementById("userlive");
const userList = document.getElementById("user-list");
const both = document.getElementById("both");
const listblock = document.getElementById("listblock");
const Users = document.getElementById("users");
const userCount = document.getElementById("user-count");
const Top = document.getElementById("UP");
const box = document.getElementById("box");
const chatside = document.getElementById("chatside");
const userside = document.getElementById("userside");
const back = document.getElementById("back");
const Newform = document.getElementById("newform");
const newChannel = document.getElementById("newchannel");
const pintab = document.getElementById("pintab");
const attachment = document.getElementById("attachment");
const pins = document.getElementById("pins");
const mediaPool = document.getElementById("mediaPool");
const download = document.getElementById("download");
const loadingCircle = document.getElementById("loading-circle");
const pinname = document.getElementById("pinname");
const content = document.getElementById("content");
const reply_id = document.getElementById("reply_id");
const media_id = document.getElementById("media_id");
const emoji_btn = document.getElementById("emoji_btn");
const emojiPallet = document.getElementById("emojiPallet");
let msgList = {};
let mediaList = {};
const emojis = [
  "😄",
  "😃",
  "😀",
  "😊",
  "☺️",
  "😉",
  "😍",
  "😘",
  "😚",
  "😗",
  "😙",
  "😜",
  "😝",
  "😛",
  "😳",
  "😁",
  "😔",
  "😌",
  "😒",
  "😞",
  "😣",
  "😢",
  "😂",
  "😭",
  "😪",
  "😥",
  "😰",
  "😅",
  "😓",
  "😩",
  "😫",
  "😨",
  "😱",
  "😠",
  "😡",
  "😤",
  "😖",
  "😆",
  "😋",
  "😷",
  "😎",
  "😴",
  "😵",
  "😲",
  "😟",
  "😦",
  "😧",
  "😈",
  "👿",
  "😮",
  "😬",
  "😐",
  "😕",
  "😯",
  "😶",
  "😇",
  "😏",
  "😑",
  "👲",
  "👳",
  "👮",
  "👷",
  "💂",
  "👶",
  "👦",
  "👧",
  "👨",
  "👩",
  "👴",
  "👵",
  "👱",
  "👼",
  "👸",
  "😺",
  "😸",
  "😻",
  "😽",
  "😼",
  "🙀",
  "😿",
  "😹",
  "😾",
  "👹",
  "👺",
  "🙈",
  "🙉",
  "🙊",
  "💀",
  "👽",
  "💩",
  "🔥",
  "✨",
  "🌟",
  "💫",
  "💥",
  "💢",
  "💦",
  "💧",
  "💤",
  "💨",
  "👂",
  "👀",
  "👃",
  "👅",
  "👄",
  "👍",
  "👎",
  "👌",
  "👊",
  "✊",
  "👋",
  "✋",
  "👐",
  "👆",
  "👇",
  "👉",
  "👈",
  "🙌",
  "🙏",
  "👏",
  "💪",
  "🚶",
  "🏃",
  "💃",
  "👫",
  "👪",
  "👬",
  "👭",
  "💏",
  "💑",
  "👯",
  "🙆",
  "🙅",
  "💁",
  "🙋",
  "💆",
  "💇",
  "💅",
  "👰",
  "🙎",
  "🙍",
  "🙇",
  "🎩",
  "👑",
  "👒",
  "👟",
  "👞",
  "👡",
  "👠",
  "👢",
  "👕",
  "👔",
  "👚",
  "👗",
  "🎽",
  "👖",
  "👘",
  "👙",
  "💼",
  "👜",
  "👝",
  "👛",
  "👓",
  "🎀",
  "🌂",
  "💄",
  "💛",
  "💙",
  "💜",
  "💚",
  "❤️",
  "💔",
  "💗",
  "💓",
  "💕",
  "💖",
  "💞",
  "💘",
  "💌",
  "💋",
  "💍",
  "💎",
  "👤",
  "👥",
  "💬",
  "👣",
  "💭",
  "🐶",
  "🐺",
  "🐱",
  "🐭",
  "🐹",
  "🐰",
  "🐸",
  "🐯",
  "🐨",
  "🐻",
  "🐷",
  "🐽",
  "🐮",
  "🐗",
  "🐵",
  "🐒",
  "🐴",
  "🐑",
  "🐘",
  "🐼",
  "🐧",
  "🐦",
  "🐤",
  "🐥",
  "🐣",
  "🐔",
  "🐍",
  "🐢",
  "🐛",
  "🐝",
  "🐜",
  "🐞",
  "🐌",
  "🐙",
  "🐚",
  "🐠",
  "🐟",
  "🐬",
  "🐳",
  "🐋",
  "🐄",
  "🐏",
  "🐀",
  "🐃",
  "🐅",
  "🐇",
  "🐉",
  "🐎",
  "🐐",
  "🐓",
  "🐕",
  "🐖",
  "🐁",
  "🐂",
  "🐲",
  "🐡",
  "🐊",
  "🐪",
  "🐆",
  "🐈",
  "🐩",
  "🐾",
  "💐",
  "🌸",
  "🌷",
  "🍀",
  "🌹",
  "🌻",
  "🌺",
  "🍁",
  "🍃",
  "🍂",
  "🌿",
  "🌾",
  "🍄",
  "🌵",
  "🌴",
  "🌲",
  "🌳",
  "🌰",
  "🌱",
  "🌼",
  "🌐",
  "🌞",
  "🌝",
  "🌚",
  "🌑",
  "🌒",
  "🌓",
  "🌔",
  "🌕",
  "🌖",
  "🌗",
  "🌘",
  "🌜",
  "🌛",
  "🌙",
  "🌍",
  "🌎",
  "🌏",
  "🌋",
  "🌌",
  "⛅",
  "⛄",
  "🌀",
  "🌁",
  "🌈",
  "🌊",
  "🌉",
  "🌇",
  "🌆",
  "🌄",
  "🌃",
  "🌍",
  "🌎",
  "🌏",
  "🌋",
  "🌌",
  "⛅",
  "⛄",
  "🌀",
  "🌁",
  "🌈",
  "🌊",
  "🌉",
  "🌇",
  "🌆",
  "🌄",
  "🌃",
  "🌂",
  "☂️",
  "☔",
  "💧",
  "💦",
  "🌊",
  "🍏",
  "🍎",
  "🍐",
  "🍊",
  "🍋",
  "🍌",
  "🍉",
  "🍇",
  "🍓",
  "🍈",
  "🍒",
  "🍑",
  "🍍",
  "🍅",
  "🍆",
  "🌽",
  "🍠",
  "🍞",
  "🍗",
  "🍖",
  "🍤",
  "🍳",
  "🍔",
  "🍟",
  "🌭",
  "🍕",
  "🍝",
  "🌮",
  "🌯",
  "🍜",
  "🍲",
  "🍥",
  "🍣",
  "🍱",
  "🍛",
  "🍙",
  "🍚",
  "🍘",
  "🍢",
  "🍡",
  "🍧",
  "🍨",
  "🍦",
  "🍰",
  "🎂",
  "🍮",
  "🍬",
  "🍭",
  "🍫",
  "🍿",
  "🍩",
  "🍪",
  "🌰",
  "🍯",
  "🍎",
  "🍏",
  "🍊",
  "🍋",
  "🍒",
  "🍇",
  "🍉",
  "🍓",
  "🍑",
  "🍈",
  "🍌",
  "🍐",
  "🍍",
  "🍠",
  "🍆",
  "🌽",
  "🍄",
  "🌰",
  "🍞",
  "🍞",
  "🍖",
  "🍗",
  "🍔",
  "🍟",
  "🌭",
  "🍕",
  "🍝",
  "🌮",
  "🌯",
  "🍜",
  "🍲",
  "🍥",
  "🍛",
  "🍙",
  "🍚",
  "🍘",
  "🍢",
  "🍡",
  "🍧",
  "🍨",
  "🍦",
  "🍰",
  "🎂",
  "🍮",
  "🍬",
  "🍭",
  "🍫",
  "🍿",
  "🍩",
  "🍪",
  "🍯",
  "🌰",
];
const reaction = ["👍", "😄", "🔥", "😱", "😋", "💢"];

emojis.forEach((emoji) => {
  let bx = document.createElement("span");
  bx.innerText = emoji;
  bx.classList.add("emoG");
  bx.setAttribute("onclick", 'add("' + emoji + '")');
  emojiPallet.appendChild(bx);
});
function updateLoadingCircle(value) {
  loadingCircle.innerText = value;
}
document.getElementById("media").addEventListener("change", function () {
  if (
    document.getElementById("media").files[0] != null &&
    pins.style.display == "none"
  ) {
    const clickEvent = new Event("click");
    attachment.dispatchEvent(clickEvent);
  }
});

let chunkSize = 51200; // 500 KB in bytes
document.getElementById("upload").onclick = async function () {
  if (document.getElementById("media").files[0] == null) {
    return;
  }
  updateLoadingCircle(0);
  document.getElementById("loading-circle").style.display = "block";
  const file = document.getElementById("media").files[0];
  const Size = file.size;
  const metaData = new FormData();
  metaData.append("name", file.name);
  metaData.append("typ", file.type);
  let offset = chunkSize;
  if (Size < offset) {
    offset = Size;
    metaData.append("dN", 1);
  }
  metaData.append("chunk", file.slice(0, offset));
  try {
    const response = await fetch("/media", {
      //first chunk
      method: "POST",
      body: metaData,
    });
    let id, hash;
    const data = await response.text();
    if (offset == Size) {
      [id, hash] = JSON.parse(data);
    } else {
      const uuid = data;
      const constsize = offset + chunkSize;
      var chunk = file.slice(offset, constsize);
      offset = constsize;
      while (offset < Size) {
        const constSize = chunkSize;
        const promise = sendSeqChunk(chunk, uuid);
        updateLoadingCircle(Math.round((offset * 100) / Size));
        chunk = file.slice(offset, offset + constSize);
        offset += constSize;
        await promise;
      }
      let res = JSON.parse(await sendSeqChunk(chunk, uuid, (dN = true))); //last chunk
      id = res[0];
      hash = res[1];
    }
    if (hash != 0) {
      if (!localStorage.getItem(hash)){
        // may be we can revoke the existing url and create a new one 
        // just in case if user has changed something then it can be refreshed
        // but currently no need
        const blob = new Blob([file.slice(0, Size)], { type: file.type });
        const url = URL.createObjectURL(blob);
        localStorage.setItem(hash, url);
      }
    }
    document.getElementById("media").value = "";
    document.getElementById("loading-circle").style.display = "none";
  } catch (error) {
    console.error("Error:", error);
  }
};
// document.getElementById("upload").onclick = async function () {
//   if (document.getElementById("media").files[0] == null) {
//     return;
//   }
//   updateLoadingCircle(0);
//   document.getElementById("loading-circle").style.display = "block";
//   const file = document.getElementById("media").files[0];
//   const Size = file.size;
//   const metaData = new FormData();
//   metaData.append("name", file.name);
//   metaData.append("typ", file.type);
//   let offset = chunkSize;
//   metaData.append("chunk", file.slice(0, offset));
//   metaData.append("uuid", "");
//   if (Size <= offset) {
//     metaData.append("dN", localStorage.getItem("server"));
//     offset = Size;
//   } else {
//     metaData.append("dN", "");
//   }
//   try {
//     const response = await fetch("/media", {
//       method: "POST",
//       body: metaData,
//     });
//     const data = await response.text();
//     let hash = data;
//     if (offset != Size) {
//       const uuid = data;
//       const constsize = offset + chunkSize;
//       var chunk = file.slice(offset, constsize);
//       offset = constsize;
//       while (offset < Size) {
//         const constSize = chunkSize;
//         const promise = sendSeqChunk(chunk, uuid);
//         updateLoadingCircle(Math.round((offset * 100) / Size));
//         chunk = file.slice(offset, offset + constSize);
//         offset += constSize;
//         await promise;
//       }

//       hash = await sendSeqChunk(chunk, uuid, (dN = true));
//     }
//     if (hash != 0) {
//       const blob = new Blob([file.slice(0, Size)], { type: file.type });
//       const url = URL.createObjectURL(blob);
//       localStorage.setItem(hash, url);
//     }
//     document.getElementById("media").value = "";
//     document.getElementById("loading-circle").style.display = "none";
//   } catch (error) {
//     console.error("Error:", error);
//   }
// };
async function sendSeqChunk(chunk, uuid, dN = false) {
  return new Promise(async (resolve, reject) => {
    try {
      const fileData = new FormData();
      fileData.append("chunk", chunk);
      fileData.append("uuid", uuid);
      if (dN) {
        fileData.append("dN", 1);
      }
      const response = await fetch("/media", {
        method: "POST",
        body: fileData,
      });
      const data = await response.text();
      if (data === "0") {
        reject("duplicate file uploaded!!!");
        loadingCircle.style.display = "none";
      }
      resolve(data);
    } catch (error) {
      console.error("Error:", error);
      reject(error);
    }
  });
}
function showfile(mime, url) {
  if (mime.toLowerCase().includes("image")) {
    const img = document.createElement("img");
    img.classList.add("image");
    img.src = url;
    content.appendChild(img);
  } else if (mime.toLowerCase().includes("video")) {
    const video = document.createElement("video");
    video.classList.add("image");
    video.controls = true;
    video.src = url;
    content.appendChild(video);
  } else if (mime.toLowerCase().includes("text")) {
    const div = document.createElement("div");
    fetch(url)
      .then((response) => response.text())
      .then((text) => {
        div.innerText = text;
      });
    div.classList.add("image");
    content.appendChild(div);
  } else {
    const embed = document.createElement("embed");
    embed.classList.add("image");
    embed.style.flexGrow = "1";
    embed.width = "100%";
    embed.height = "100%";
    embed.type = mime;
    embed.src = url;
    content.appendChild(embed);
  }
}
function showpinned(id) {
  const hash=mediaList[id][0]
  const media_data=mediaList[id][1]
  if (pinname.dataset.key == hash) {
    return;
  }
  body.classList.add("blur");
  pintab.style.display = "block";
  pinname.innerText = media_data[0];
  pinname.setAttribute("data-key", hash);
  content.innerHTML = "";
  let url = localStorage.getItem(hash);
  if (!url) {
    // loading new media
    fetch("/media/" + id.toString())
      .then((response) => {
        if (response.status == 200) {
          return response.blob();
        } else {
          content.innerHTML =
            "<h style='color:wheat;'>Please reupload this file.</h>";
          setTimeout(() => {
            cancelpinned();
          }, 2000);
          throw new Error("Please reupload this file.");
        }
      })
      .then((Data) => {
        if (Data.length != 0) {
          //cant rely on server for mimetype
          const Data_with_mime = new Blob([Data], { type: media_data[1] });
          url = URL.createObjectURL(Data_with_mime);
          localStorage.setItem(hash, url);
          showfile(media_data[1], url);
        }
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  } else {
    showfile(media_data[1], url);
  }
}
function cancelpinned() {
  pintab.style.display = "none";
  pinname.innerText = "";
  pinname.dataset.key = "";
  body.classList.remove("blur");
  content.innerHTML = "";
}
makeHoverable(attachment, pins);

function add(emoji) {
  if (chatside.style.display == "block") {
    message_input.value += emoji + " ";
  } else {
    newChannel.value += emoji + " ";
  }
}
function rearrange() {
  search = search_input.value.toLowerCase();
  search_input.value = "";
  Array.from(document.getElementsByClassName("name")).forEach((name) => {
    if (name.innerText.toLowerCase().includes(search)) {
      channel_list.insertAdjacentElement(
        "afterbegin",
        name.parentElement.parentElement
      );
    }
  });
}
function gethistory() {
  socket.emit("getHistory");
}
function show(side) {
  if (side === "chatside") {
    if (chatside.style.display === "none") {
      userside.style.display = "none";
      chatside.style.display = "block";
      back.style.display = "block";
    }
  } else {
    if (userside.style.display === "none") {
      chatside.style.display = "none";
      userside.style.display = "block";
      back.style.display = "none";
      chatbox.innerHTML = "";
      if (document.getElementsByClassName("active").length != 0) {
        document.getElementsByClassName("active")[0].classList.remove("active");
      }
    }
  }
}
function emphasize() {
  show("chatside");
  chatbox.innerHTML = "";
  userList.innerHTML = "";
}
function goto(This) {
  let active = document.getElementsByClassName("active");
  if (active.length != 0) {
    if (active[0] != This.firstElementChild) {
      active[0].classList.remove("active");
    } else {
      return;
    }
  }
  This.firstElementChild.classList.add("active");
  topic.innerText = This.innerText.split("\n")[0];
  emphasize();
  B4Change(This.firstElementChild);
  msgList = {};
  const to = This.classList[0].split("-");
  if (to[0] == "c") {
    socket.emit("change", { channel: This.classList[0].split("-")[1] });
  } else {
    socket.emit("change", { Frnd: This.classList[0].split("-")[1] });
  }
}
function B4Change(to) {
  if (to.childElementCount == 3) {
    to.children[2].remove();
  }
  chatbox.innerHTML = "";
  userList.innerHTML = "";
  userCount.innerText = "(...)";
  message_input.value = "";
  if (listblock.style.display == "block") {
    const clickEvent = new Event("click");
    Users.dispatchEvent(clickEvent);
  }
  if (pins.style.display == "block") {
    const clickEvent = new Event("click");
    attachment.dispatchEvent(clickEvent);
  }
  if (emojiPallet.style.display == "block") {
    const clickEvent = new Event("click");
    emoji_btn.dispatchEvent(clickEvent);
  }
}
function gotoserver(Newserver) {
  console.log(Newserver)
  console.log(Newserver.firstElementChild.innerText)
  // console.log(Newserver.innerText)
  // if (Newserver.parentElement.childElementCount==3){
  //   Newserver.parentElement.lastElementChild.remove()
  // }
  if (localStorage.getItem('server') != Newserver.firstElementChild.innerText) {
    B4Change(Newserver);
    mediaPool.innerHTML = "";
    socket.emit("changeServer", Newserver.innerText);
  }
}
makeHoverable(Users, listblock);

makeHoverable(emoji_btn, emojiPallet);
function makeHoverable(btn, block) {
  let visibility = true;
  let time;
  let mouseleave = function () {
    time = setTimeout(() => {
      block.style.display = "none";
      btn.style.color = "black";
    }, 100);
  };
  let blockenter = function () {
    clearTimeout(time);
    block.style.display = "block";
    btn.style.color = "aquamarine";
  };
  let btnenter = function () {
    clearTimeout(time);
    block.style.display = "block";
    btn.style.color = "aquamarine";
  };
  btn.addEventListener("mouseenter", btnenter);
  btn.addEventListener("mouseleave", mouseleave);
  block.addEventListener("mouseenter", blockenter);
  block.addEventListener("mouseleave", mouseleave);

  btn.addEventListener("click", () => {
    clearTimeout(time);
    if (visibility) {
      block.style.display = "block";
      btn.style.color = "aquamarine";
      btn.removeEventListener("mouseenter", btnenter);
      btn.removeEventListener("mouseleave", mouseleave);
      block.removeEventListener("mouseenter", blockenter);
      block.removeEventListener("mouseleave", mouseleave);
      visibility = false;
    } else {
      btn.addEventListener("mouseenter", btnenter);
      btn.addEventListener("mouseleave", mouseleave);
      block.addEventListener("mouseenter", blockenter);
      block.addEventListener("mouseleave", mouseleave);
      block.style.display = "none";
      btn.style.color = "black";
      visibility = true;
    }
  });
}
socket.on("connect", function () {
  localStorage.setItem("server", document.getElementById("server").innerText);
  socket.emit("Load");
});
function addmedia(data) {
  //data = [id,hash,name]
  mediaList[data[0]] = [data[1], data[2]];
  const mediaplate = document.createElement("div");
  const nameplate = document.createElement("div");
  nameplate.classList.add("pinned");
  const name = data[2]; //name=[name,mime]
  nameplate.innerText = name[0];
  nameplate.setAttribute("onclick", "showpinned(" + data[0] + ")");
  const forward = document.createElement("div");
  forward.classList.add("forward");
  forward.setAttribute("onclick", 'reply("' + name[0] + '","' + data[0] + '")');
  mediaplate.classList.add("mediatitle");
  mediaplate.appendChild(nameplate);
  mediaplate.appendChild(forward);
  mediaplate.classList.add("M-" + data[0]);
  mediaPool.appendChild(mediaplate);
}
socket.on("medias", function (datas) {
  mediaList = {};
  datas.forEach((data) => {
    addmedia([data[0], data[1], JSON.parse(data[2])]);
  });
});
socket.on("media", function (data) {
  console.log(data)
  addmedia(data);
});
socket.on("showNewServer", function (data) {
  server.innerText = data[0];
  document.getElementById("server2").innerText = data[0];
  if (data[0] != "app") {
    download.href = "/download/" + data[0];
    download.style.visibility = "visible";
  } else {
    download.href = "#";
    download.style.visibility = "hidden";
  }
  localStorage.setItem("server", data[0]);
  show("userside");
  all = false;
  channel_list.innerHTML = "";
  for (let i = data[1].length - 1; i > -1; i--) {
    showing(data[1][i]);
  }
});
document.getElementById("back").onclick = function () {
  userList.innerHTML = "";
  userCount.innerText = "(...)";
  message_input.value = "";
  document.getElementById("topic").innerText = "";
  document.getElementById("chats").innerHTML = "";

  show("userside");
  socket.emit("change", 0);
};
function makeMessage(id, bool, neu) {
  const msg = msgList[id];
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
  if (msg[2]) {
    const replyof = document.createElement("div");
    const repid = msg[2];
    if (msgList[repid]) {
      const sender = msgList[repid][5];
      let repmsg = msgList[repid][0];
      if (!repmsg) {
        repmsg = "";
      }
      replyof.innerText = sender + ": " + repmsg;
      if (msgList[repid][1]) {
        replyof.innerText += "\n media";
      }
      replyof.setAttribute("onclick", "Focus(" + repid + ")");
    } else replyof.innerText = "please go back";
    replyof.classList.add("reply");
    msgPara.appendChild(replyof);
  }
  if (msg[1]) {
    const m = mediaList[msg[1]];
    // const m = document.getElementsByClassName("M-" + msg[1])[0];
    if (m) {
      const mediatitle = document.createElement("div");
      const nameplate = document.createElement("div");
      nameplate.classList.add("pinned");
      nameplate.classList.add("msg");
      const medianame = m[1][0];
      const hash = m[0];
      nameplate.innerText = medianame;
      nameplate.setAttribute("onclick", "showpinned(" + msg[1] + ")");
      mediatitle.appendChild(nameplate);
      // const forward=document.createElement('div')
      // forward.classList.add('forward')
      // forward.setAttribute(
      //   "onclick",
      //   'reply("' + medianame + '","' + msg[1] + '")'
      // );
      // mediatitle.appendChild(forward)
      mediatitle.classList.add("mediatitle");
      msgPara.appendChild(mediatitle);
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
  if (neu) {
    chatbox.appendChild(message);
  } else {
    chatbox.insertAdjacentElement("afterbegin", message);
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
}

socket.on("showMessages", function (Msgs) {
  ID = Msgs.pop();
  if (ID == 0) {
    Top.style.visibility = "hidden";
  } else {
    Top.style.visibility = "visible";
  }
  const prvt = Msgs.pop();
  localStorage.setItem("prvt", prvt);
  Mess = document.getElementsByClassName("message")[0];
  //  make an object store for each channel and prvt chat
  if (prvt != null) {
    for (var i = 0; i < Msgs.length; i++) {
      const data = JSON.parse(Msgs[i][1]);
      if (data[5] == prvt) {
        data[5] = name;
      } else {
        data[5] = topic.innerText;
      }
      msgList[Msgs[i][0]] = data;
    }
    for (var i = 0; i < Msgs.length; i++) {
      if (msgList[Msgs[i][0]][5] == name) {
        makeMessage(Msgs[i][0], true, false);
      } else {
        makeMessage(Msgs[i][0], false, false);
      }
    }
  } else {
    for (var i = 0; i < Msgs.length; i++) {
      const data = JSON.parse(Msgs[i][2]);
      data[5] = Msgs[i][0];
      msgList[Msgs[i][1]] = data;
    }
    for (var i = 0; i < Msgs.length; i++) {
      if (Msgs[i][0] == name) {
        makeMessage(Msgs[i][1], true, false);
      } else {
        makeMessage(Msgs[i][1], false, false);
        if (i == Msgs.length - 1 || Msgs[i][0] != Msgs[i + 1][0]) {
          var Frnd = document.createElement("div");
          Frnd.classList.add("message");
          Frnd.classList.add("frnd");
          Frnd.innerHTML = '<p onclick = GOTOfrnd("' + Msgs[i][0] + '")></p>';
          var frndname = document.createElement("div");
          frndname.innerText = Msgs[i][0];
          Frnd.firstChild.appendChild(frndname);
          chatbox.insertAdjacentElement("afterbegin", Frnd);
        }
      }
    }
  }
  if (Mess) {
    Mess.scrollIntoView();
    if (Mess.classList.contains("frnd") && Mess.innerText == Msgs[0][0]) {
      Mess.remove();
    }
  } else {
    box.scrollTop = box.scrollHeight;
  }
});
function Focus(id) {
  const to = document.getElementsByClassName("m-" + id)[0];
  if (to) {
    to.scrollIntoView();
    to.style.background = "pink";
    setTimeout(() => {
      to.style.background = "";
    }, 750);
  }
}
function react(emoji, id) {
  socket.emit("reaction", [id, emoji]);
}
function showmoremenu(message) {
  if (message.childElementCount == 2) {
    message.lastElementChild.style.display = "none";
    const moremenu = document.createElement("div");
    moremenu.classList.add("moremenutab");
    const gap = message.firstChild.clientWidth + 4 + "px";
    if (message.classList.contains("my_message")) {
      moremenu.style.right = gap;
    } else {
      moremenu.style.left = gap;
    }
    moremenu.innerHTML =
      '<div class="moremenuoptions" onclick="reply(null,' +
      message.firstChild.classList[0].split("-")[1] +
      ')">Reply</div><div class="moremenuoptions">Copy</div>';
    message.appendChild(moremenu);
    moremenu.style.display = "block";
    var done = true;
    document.addEventListener("click", function e(event) {
      if (!done) {
        document.removeEventListener("click", e);
        moremenu.remove();
        if (!message.contains(event.target)) {
          message.firstChild.firstChild.style.display = "none";
        }
      } else {
        done = false;
      }
    });
  } else {
    message.lastElementChild.remove();
    message.lastElementChild.style.display = "block";
  }
}
function reply(media = null, id) {
  if (chatinput.childElementCount == 1) {
    const plate = document.createElement("div");
    plate.classList.add("replydiv");
    box.style.height = "70vh";
    plate.innerHTML =
      '<p class="replyplate"><small>for reply</small></p><button class="replydelete" onclick="removereply()">X</button><p class="replyplate"><small>for attachment</small></p><button class="replydelete" onclick="removeattach()">X</button>';
    chatinput.insertAdjacentElement("afterbegin", plate);
    if (!media) {
      reply_id.value = id;
      plate.firstChild.innerText =
        "Reply:\n" + msgList[id][0] + "  " + msgList[id][3];
    } else {
      media_id.value = id;
      plate.children[2].innerText = "Attach:\n" + media;
    }
  } else {
    if (media == null) {
      reply_id.value = id;
      chatinput.firstChild.firstChild.innerText =
        "Reply:\n" + msgList[id][0] + "  " + msgList[id][3];
    } else {
      media_id.value = id;
      chatinput.firstChild.children[2].innerText = "Attach:\n" + media;
    }
  }
}
function removeattach() {
  media_id.value = "";
  const replydiv = document.getElementsByClassName("replydiv")[0];
  if (replydiv.childElementCount == 4) {
    replydiv.lastChild.remove();
    replydiv.lastChild.remove();
  } else {
    replydiv.remove();
    box.style.height = "74vh";
  }
}
function removereply() {
  reply_id.value = "";
  const replydiv = document.getElementsByClassName("replydiv")[0];
  if (replydiv.childElementCount == 4) {
    replydiv.firstChild.remove();
    replydiv.firstChild.remove();
  } else {
    replydiv.remove();
    box.style.height = "74vh";
  }
}
function showreactions(message) {
  if (message.childElementCount == 2) {
    const tab = document.createElement("div");
    tab.classList.add("reactiontab");
    reaction.forEach((emoji) => {
      const blk = document.createElement("div");
      blk.classList.add("emoG");
      blk.innerText = emoji;
      blk.setAttribute(
        "onclick",
        'react("' +
          emoji +
          '",' +
          message.firstChild.classList[0].split("-")[1] +
          ")"
      );
      tab.appendChild(blk);
    });
    message.appendChild(tab);
    var done = true;
    document.addEventListener("click", function e(event) {
      if (!done) {
        document.removeEventListener("click", e);
        message.lastElementChild.remove();
        if (!message.contains(event.target)) {
          message.lastChild.style.display = "none";
        }
      }
      if (done && event.target == message.children[1]) {
        done = false;
      }
    });
  }
}
function GOTOfrnd(user, GOTO = true) {
  const frnd = document.getElementsByClassName("f-" + user)[0];
  if (!frnd) {
    const friend = document.createElement("div");
    friend.classList.add("f-" + user);
    friend.setAttribute("onclick", "goto(this)");
    const block = document.createElement("div");
    block.classList.add("block");
    block.innerHTML =
      '<div class="imgbx"><img src="/static/person.png" alt="pic" class="cover"></div><div class="details"><div class="name">' +
      user +
      "</div></div>";
    friend.appendChild(block);
    const isActive = document.getElementsByClassName("active")[0];
    if (isActive && isActive.parentElement == channel_list.firstElementChild) {
      channel_list.insertBefore(
        friend,
        isActive.parentElement.nextElementSibling
      );
    } else {
      channel_list.insertAdjacentElement("afterbegin", friend);
      friend.scrollIntoView();
    }
    if (GOTO) {
      goto(friend);
    }
  }
  if (GOTO) {
    goto(frnd);
  }
}
socket.on("show_message", function (data) {
  // TO ADD NEW CHILD OF MESSAGE //
  if (data.length == 2) {
    const msg = JSON.parse(data[1]);
    if (JSON.stringify(msg[5]) == localStorage.getItem("prvt")) {
      msg[5] = name;
      msgList[data[0]] = msg;
      makeMessage(data[0], true, true);
    } else {
      msg[5] = topic.innerText;
      msgList[data[0]] = msg;
      makeMessage(data[0], false, true);
    }
  } else {
    const msg = JSON.parse(data[2]);
    msg[5] = data[1];
    msgList[data[1]] = msg;
    if (data[0] == name) {
      makeMessage(data[1], true, true);
    } else {
      if (msgList.length == 0 || msgList[data[1] - 1][5] != data[0]) {
        const Frnd = document.createElement("div");
        Frnd.classList.add("message");
        Frnd.classList.add("frnd");
        Frnd.innerHTML = "<p></p>";
        const frndname = document.createElement("div");
        frndname.innerText = data[0];
        Frnd.firstChild.appendChild(frndname);
        Frnd.setAttribute("onclick", 'GOTOfrnd("' + data[0] + '")');
        chatbox.appendChild(Frnd);
      }
      makeMessage(data[1], false, true);
    }
  }
  box.scrollTop = box.scrollHeight;
});
socket.on("reaction", function (reactData) {
  const myreaction = document.getElementsByClassName(
    "m-" + reactData[0] + "r-" + reactData[1]
  )[0];
  if (myreaction) {
    myreaction.innerText = reactData[2];
  } else {
    const reaction = document.getElementsByClassName("r-" + reactData[0])[0];
    if (reaction) {
      const EMOG = document.createElement("div");
      EMOG.classList.add("m-" + reactData[0] + "r-" + reactData[1]);
      EMOG.innerText = reactData[2];
      EMOG.classList.add("react");
      if (reactData[1] == userid) {
        EMOG.classList.add("myreaction");
      }
      reaction.appendChild(EMOG);
    } else {
      const message = document.getElementsByClassName("m-" + reactData[0])[0];
      if (message) {
        const reactionpallet = document.createElement("div");
        reactionpallet.classList.add("reactions");
        reactionpallet.classList.add("r-" + reactData[0]);
        const EMOG = document.createElement("div");
        EMOG.classList.add("m-" + reactData[0] + "r-" + reactData[1]);
        EMOG.innerText = reactData[2];
        EMOG.classList.add("react");
        if (reactData[1] == userid) {
          EMOG.classList.add("myreaction");
        }
        reactionpallet.appendChild(EMOG);
        message.appendChild(reactionpallet);
      }
    }
  }
});
message_form.onsubmit = function () {
  let message = message_input.value.trim();
  if (message.length == 0) {
    if (!media_id.value) {
      return false;
    }
  }
  let msg = { 0: message };
  if (media_id.value || reply_id.value) {
    document.getElementsByClassName("replydiv")[0].remove();
    box.style.height = "74vh";
  }
  if (reply_id.value) {
    msg[2] = reply_id.value;
    reply_id.value = "";
  }
  if (media_id.value) {
    msg[1] = media_id.value;
    media_id.value = "";
  }
  channel_list.insertAdjacentElement(
    "afterbegin",
    document.getElementsByClassName("active")[0].parentElement
  );
  socket.emit("message", msg);
  message_input.value = "";
  return false;
};
socket.on("serverlive", function (userObj) {
  userlive.innerHTML = "";
  for (const key in userObj) {
    let user = document.createElement("li");
    user.innerText = key;
    user.setAttribute("onclick", 'GOTOfrnd("' + key + '")');
    userlive.appendChild(user);
  }
});
socket.on("notify", function (userObj) {
  userList.innerHTML = "";
  for (const key in userObj) {
    let user = document.createElement("li");
    user.innerText = key;
    user.setAttribute("onclick", 'GOTOfrnd("' + key + '")');
    userList.appendChild(user);
  }
  userCount.innerText = " (" + Object.keys(userObj).length + ")";
});
function shownotification(to, name) {
  console.log(to+name)
  const notify = document.getElementsByClassName(to + name)[0]
    .firstElementChild;
  if (notify) {
    if (notify.childElementCount != 3) {
      let num = document.createElement("p");
      num.classList.add("update");
      num.innerText = "1";
      notify.appendChild(num);
    } else {
      let num = parseInt(notify.children[2].innerText);
      notify.children[2].innerText = num + 1;
    }
    if(to!="s-"){
      const isActive = document.getElementsByClassName("active")[0];
      if (isActive && isActive.parentElement == channel_list.firstElementChild) {
        channel_list.insertBefore(
          notify.parentElement,
          isActive.parentElement.nextElementSibling
        );
      } else {
        channel_list.insertAdjacentElement("afterbegin", notify.parentElement);
        notify.scrollIntoView();
      }
    }
  }
}
socket.on("dm", function (data) {
  GOTOfrnd(data, (GOTO = false));
  shownotification("f-", data);
});
socket.on("otherupdate", function (data) {
  shownotification("s-", data);
});
socket.on("currupdate", function (data) {
  shownotification("c-", data);
});
search_form.onsubmit = function () {
  let search = search_input.value.trim();
  if (search.length != 0) {
    if (search == "*") {
      search = "";
      all = true;
    }
    socket.emit("search_text", String(search));
    rearrange();
  }
  return false;
};
Newform.onsubmit = function () {
  let chnl = newchannel.value.trim();
  if (chnl.length) {
    socket.emit("create", chnl);
    newchannel.value = "";
  }
  return false;
};
socket.on("show_this", function (data) {
  if (data.hasOwnProperty("users")) {
    data["users"].forEach((user) => {
      GOTOfrnd(user, false);
    });
  } else {
    data["channel"];
    showing(data["channel"]);
  }
});
function showing(data) {
  const channel = document.createElement("div");
  channel.setAttribute("onclick", "goto(this)");
  channel.classList.add("c-" + data[0]);
  const block = document.createElement("div");
  block.classList.add("block");
  block.innerHTML =
    '<div class="imgbx"><img src="/static/profile.webp" alt="pic" class="cover"></div><div class="details"><div class="name">' +
    data[1] +
    '</h4></div><div class="creator"><p>created by ' +
    data[2] +
    '</p><!-- <b onclick="location.href="/delete">x</b> --></div></div>';
  channel.appendChild(block);
  const isActive = document.getElementsByClassName("active")[0];
  if (isActive && isActive.parentElement == channel_list.firstElementChild) {
    channel_list.insertBefore(
      channel,
      isActive.parentElement.nextElementSibling
    );
  } else {
    channel_list.insertAdjacentElement("afterbegin", channel);
    channel.scrollIntoView();
  }
}

localStorage.clear();

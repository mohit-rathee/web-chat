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
const loadingCircle = document.getElementById("loading-circle");
const pinname = document.getElementById("pinname");
const content = document.getElementById("content");
const emoji_btn = document.getElementById("emoji_btn");
const emojiPallet = document.getElementById("emojiPallet");
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

function updateLoadingCircle(value) {
  loadingCircle.innerText = value;
}
let chunkSize = 102400; // 100 KB in bytes
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
  metaData.append("chunk", file.slice(0, offset));
  metaData.append("uuid", "");
  if (Size <= offset) {
    metaData.append("dN", localStorage.getItem("server"));
    offset = Size;
  } else {
    metaData.append("dN", "");
  }
  try {
    const response = await fetch("/media", {
      method: "POST",
      body: metaData,
    });
    const data = await response.text();
    let hash = data;
    console.log("Response:", data);
    if (offset != Size) {
      const uuid = data;
      console.log(Size);
      const constsize=offset+chunkSize
      var chunk = file.slice(offset, constsize);
      offset =constsize;
      while (offset < Size) {
        const constSize=chunkSize;
        console.log(offset);
        const promise = sendSeqChunk(chunk, uuid);
        updateLoadingCircle(Math.round((offset * 100) / Size));
        chunk = file.slice(offset, offset + constSize);
        offset += constSize;
        await promise;
      }
       console.log("last chunk") 
       console.log(offset)


      hash = await sendSeqChunk(chunk, uuid, (dN = true));
    }
    console.log(hash);
    if (hash != 0) {
      const blob = new Blob([file.slice(0, Size)], { type: file.type });
      const url = URL.createObjectURL(blob);
      console.log(url);
      localStorage.setItem(hash, url);
    }
    document.getElementById("media").value = "";
    document.getElementById("loading-circle").style.display = "none";
  } catch (error) {
    console.error("Error:", error);
  }
};

async function sendSeqChunk(chunk, uuid, dN = false) {
  return new Promise(async (resolve, reject) => {
    try {
      const fileData = new FormData();
      fileData.append("chunk", chunk);
      fileData.append("uuid", uuid);
      if (!dN) {
        fileData.append("dN", "");
      } else {
        fileData.append("dN", localStorage.getItem("server"));
        console.log(localStorage.getItem("server"));
      }
      const response = await fetch("/media", {
        method: "POST",
        body: fileData,
      });
      const data = await response.text();
      if (data=="0"){
        reject("file reuploaded!!!")
        loadingCircle.style.display="none"
      }
      resolve(data)

    } catch (error) {
      console.error("Error:", error);
      reject(error);
    }
  });
}
function showfile(mime, url) {
  console.log("showing file");
  if (mime.toLowerCase().includes("image")) {
    console.log("showing image file");
    const img = document.createElement("img");
    img.classList.add("image");
    img.src = url;
    content.appendChild(img);
  } else if (mime.toLowerCase().includes("video")) {
    console.log("showing video file");
    const video = document.createElement("video");
    video.classList.add("image");
    video.controls = true;
    video.src = url;
    content.appendChild(video);
  } else if (mime.toLowerCase().includes("text")) {
    console.log("showing div file");
    const div = document.createElement("div");
    fetch(url)
      .then((response) => response.text())
      .then((text) => {
        div.innerText = text;
      });
    div.classList.add("image");
    content.appendChild(div);
  } else {
    console.log("showing div file");
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

function showpinned(data) {
  if (pinname.dataset.key == data[1]) {
    return;
  }
  body.classList.add("blur");
  pintab.style.display = "block";
  pinname.innerText = data[0];
  pinname.setAttribute("data-key", data[1]);
  content.innerHTML = "";
  let url = localStorage.getItem(data[1]);
  if (!url) {
    // key doesnot exist
    console.log(
      "sending request to " +
        "/" +
        localStorage.getItem("server") +
        "/" +
        data[1].toString()
    );
    fetch("/" + localStorage.getItem("server") + "/" + data[1].toString())
      .then((response) => response.blob())
      .then((Data) => {
        // geneate url
        url = URL.createObjectURL(Data);
        // store this url
        console.log(url);
        localStorage.setItem(data[1], url);
        showfile(data[2], url);
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  } else {
    showfile(data[2], url);
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

emojis.forEach((emoji) => {
  let bx = document.createElement("span");
  bx.innerText = emoji;
  bx.classList.add("emoG");
  bx.setAttribute("onclick", 'add("' + emoji + '")');
  emojiPallet.appendChild(bx);
});

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

function goto(Newchannel) {
  let active = document.getElementsByClassName("active");
  if (active[0] != Newchannel) {
    if (active.length != 0) {
      active[0].classList.remove("active");
    }
    Newchannel.classList.add("active");
    document.getElementById("topic").innerText =
      Newchannel.innerText.split("\n")[0];
    emphasize();
    // define a new funtion
    B4Change(Newchannel);
    socket.emit("change", { channel: Newchannel.dataset.key });
  }
}

function gotofrnd(Frnd) {
  let active = document.getElementsByClassName("active");
  if (active[0] != Frnd) {
    if (active.length != 0) {
      active[0].classList.remove("active");
    }
    Frnd.classList.add("active");
    if (Frnd.childElementCount == 3) {
      Frnd.children[2].remove();
    }
    document.getElementById("topic").innerText = Frnd.innerText;
    emphasize();
    socket.emit("change", { Frnd: Frnd.innerText });
  }
}

function B4Change(to) {
  if (to.childElementCount == 3) {
    to.children[2].remove();
  }
  chatbox.innerHTML = "";
  listvisibility = true;
  userList.innerHTML = "";
  userCount.innerText = "(...)";
  message_input.value = "";
  pinsvisibility = true;
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
  console.log("changing server");
  if (server.innerText != Newserver.innerText) {
    console.log(Newserver);
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
  let mediaplate = document.createElement("div");
  mediaplate.classList.add("pinned");
  mediaplate.innerText = data[0];

  mediaplate.setAttribute(
    "onclick",
    "showpinned(" + JSON.stringify(data) + ")"
  );
  mediaPool.appendChild(mediaplate);
}

socket.on("medias", function (datas) {
  datas.forEach((data) => {
    addmedia(data);
  });
});

socket.on("media", function (data) {
  addmedia(data);
});

socket.on("showNewServer", function (data) {
  server.innerText = data[0];
  document.getElementById("server2").innerText = data[0];
  document.getElementById("download").href = "/download/" + data[0];
  localStorage.setItem("server", data[0]);
  show("userside");
  all = false;
  channel_list.innerHTML = "";
  data[1].forEach((element) => {
    let channel = document.createElement("div");
    channel.classList.add("block");
    channel.innerHTML =
      '<div class="imgbx"><img src="/static/profile.webp" alt="pic" class="cover"></div><div class="details"><div class="name"><h4 data-key="' +
      element[0] +
      '" class="chnl">' +
      element[1] +
      '</h4></div><div class="creator"><p>created by ' +
      element[2] +
      "</p></div></div>";
    channel.setAttribute("data-key", element[0]);
    channel.setAttribute("onclick", "goto(this)");
    channel_list.appendChild(channel);
  });
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

socket.on("showMessages", function (Msgs) {
  ID = Msgs.pop();
  if (ID == 0) {
    Top.style.visibility = "hidden";
  } else {
    Top.style.visibility = "visible";
  }
  Mess = document.getElementsByClassName("message")[0];
  for (var i = 0; i < Msgs.length; i++) {
    var message = document.createElement("div");
    message.classList.add("message");
    if (Msgs[i][0] == name) {
      message.classList.add("my_message");
      message.innerHTML = "<p></p>";
      var text = document.createElement("div");
      text.innerText = Msgs[i][1];
      message.firstChild.appendChild(text);
      var time = document.createElement("span");
      time.innerText = Msgs[i][2];
      message.firstChild.appendChild(time);
      chatbox.insertAdjacentElement("afterbegin", message);
    } else {
      message.classList.add("frnd_message");
      message.innerHTML = "<p></p>";
      var text = document.createElement("div");
      text.innerText = Msgs[i][1];
      message.firstChild.appendChild(text);
      var time = document.createElement("span");
      time.innerText = Msgs[i][2];
      message.firstChild.appendChild(time);
      if (i == Msgs.length - 1 || Msgs[i][0] != Msgs[i + 1][0]) {
        var Frnd = document.createElement("div");
        Frnd.classList.add("message");
        Frnd.classList.add("frnd");
        Frnd.innerHTML = "<p></p>";
        var frndname = document.createElement("div");
        frndname.innerText = Msgs[i][0];
        Frnd.firstChild.appendChild(frndname);
        Frnd.setAttribute("onclick", 'GOTOfrnd("' + Msgs[i][0] + '")');
        chatbox.insertAdjacentElement("afterbegin", message);
        chatbox.insertAdjacentElement("afterbegin", Frnd);
        // chatbox.insertBefore(Frnd, Top);
      } else {
        chatbox.insertAdjacentElement("afterbegin", message);
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

function GOTOfrnd(user, GOTO = true) {
  let block = document.getElementsByClassName("friend");
  let create = true;
  for (let i = 0; i < block.length; i++) {
    if (block[i].innerText == user) {
      if (GOTO) {
        gotofrnd(block[i].parentElement);
        return;
      }
      create = false;
    }
  }
  if (create) {
    let plate = document.createElement("div");
    plate.classList.add("block");
    plate.innerHTML =
      '<div class="imgbx"><img src="/static/person.png" alt="pic" class="cover"></div><div class="details"><div class="name"><h4 class="friend" data-key="' +
      user +
      '">' +
      user +
      "</h4></div></div></div>";
    plate.setAttribute("onclick", "gotofrnd(this)");
    channel_list.insertAdjacentElement("afterbegin", plate);
    if (GOTO) {
      gotofrnd(plate);
    }
    return;
  }
}
socket.on("show_message", function (data) {
  // TO ADD NEW CHILD OF MESSAGE //
  let chat = document.createElement("div");
  chat.classList.add("message");
  if (data[0] == name) {
    chat.classList.add("my_message");
  } else {
    chat.classList.add("frnd_message");
    var LM = document.getElementsByClassName("frnd");
    if (LM.length == 0 || LM[LM.length - 1].innerText != data[0]) {
      var Frnd = document.createElement("div");
      Frnd.classList.add("message");
      Frnd.classList.add("frnd");
      Frnd.innerHTML = "<p></p>";
      var frndname = document.createElement("div");
      frndname.innerText = data[0];
      Frnd.firstChild.appendChild(frndname);
      Frnd.setAttribute("onclick", 'GOTOfrnd("' + data[0] + '")');
      chatbox.appendChild(Frnd);
    }
  }
  chat.innerHTML = "<p></p>";
  var text = document.createElement("div");
  text.innerText = data[1];
  var time = document.createElement("span");
  time.innerText = data[2];
  chat.firstChild.appendChild(text);
  chat.firstChild.appendChild(time);
  chatbox.appendChild(chat);
  chat.scrollIntoView();
});
message_form.onsubmit = function () {
  let message = message_input.value.trim();
  if (message.length) {
    channel_list.insertAdjacentElement(
      "afterbegin",
      document.getElementsByClassName("active")[0]
    );
    socket.emit("recieve_message", String(message));
    message_input.value = "";
  }
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
  let ls = document.getElementsByClassName(to);
  for (let i = 0; i < ls.length; i++) {
    if (ls[i].dataset.key == name) {
      console.log(ls[i]);
      const block = ls[i].parentElement.parentElement.parentElement;
      if (block.childElementCount != 3) {
        let num = document.createElement("p");
        num.classList.add("update");
        num.innerText = "1";
        block.appendChild(num);
      } else {
        let num = parseInt(block.children[2].innerText);
        block.children[2].innerText = num + 1;
      }
      block.parentElement.insertAdjacentElement("afterbegin", block);
    }
  }
}

socket.on("dm", function (data) {
  GOTOfrnd(data, (GOTO = false));
  shownotification("friend", data);
});
socket.on("otherupdate", function (data) {
  shownotification("SERVER", data);
});
socket.on("currupdate", function (data) {
  shownotification("chnl", data);
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
      GOTOfrnd(user, (GOTO = false));
    });
  } else {
    const channel = document.createElement("div");
    channel.classList.add("block");
    channel.innerHTML =
      '<div class="imgbx"><img src="/static/profile.webp" alt="pic" class="cover"></div><div class="details"><div class="name"><h4 data-key=' +
      data["channel"][0] +
      ' class="chnl">' +
      data["channel"][1] +
      '</h4></div><div class="creator"><p>created by ' +
      data["channel"][2] +
      '</p><!-- <b onclick="location.href="/delete">x</b> --></div></div>';
    channel.setAttribute("data-key", data["channel"][0]);
    channel.setAttribute("onclick", "goto(this)");
    channel_list.insertAdjacentElement("afterbegin", channel);
  }
});
localStorage.clear();

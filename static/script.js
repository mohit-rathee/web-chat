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
const Info = document.getElementById("Info")
const Users = document.getElementById("users");
const userCount = document.getElementById("user-count");
const Top = document.getElementById("UP");
const box = document.getElementById("box");
const chatside = document.getElementById("chatside");
const userside = document.getElementById("userside");
const threeDot = document.getElementById("3dot");
const options = document.getElementById("options");
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
const servers = document.getElementById("servers");
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
  metaData.append("server", localStorage.getItem("server"));
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
      if (!localStorage.getItem(hash)) {
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
};
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
function showpinned(id, hash, name, mime) {
  if (pinname.dataset.key == id) {
    return;
  }
  body.classList.add("blur");
  pintab.style.display = "block";
  pinname.innerText = name;
  pinname.setAttribute("data-key", id);
  content.innerHTML = "";
  let url = localStorage.getItem(hash);
  if (!url) {
    // loading new media
    fetch("/media/" + localStorage.getItem("server") + "/" + id.toString())
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
          const Data_with_mime = new Blob([Data], { type: mime });
          url = URL.createObjectURL(Data_with_mime);
          localStorage.setItem(hash, url);
          showfile(mime, url);
        }
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  } else {
    showfile(mime, url);
  }
}
function cancelpinned() {
  pintab.style.display = "none";
  pinname.innerText = "";
  pinname.dataset.key = "";
  body.classList.remove("blur");
  content.innerHTML = "";
}
function createChannel() {
  search_input.placeholder = "New Channel Name";
  search_input.focus();
  search_input.style.border = "2px solid aliceblue";
  search_form.setAttribute("data-create", "y");
  let done = true;
  document.addEventListener("click", function e(event) {
    if (!done) {
      if (event.target.classList.contains("emoG")||event.target==emoji_btn|| event.target==search_input) {
        return;
      } else {
        document.removeEventListener("click", e);
        search_input.placeholder = "Search Channel";
        search_form.setAttribute("data-create", "n");
        search_input.style.border = "none";
      }
    } else {
      done = false;
    }
  });
}
function add(emoji) {
  if (search_form.dataset.create == "n") {
    message_input.value += emoji + " ";
  } else {
    search_input.value += emoji + " ";
  }
}
function rearrange(chnlName) {
  chnlName = chnlName.toLowerCase();
  Array.from(document.getElementsByClassName("name")).forEach((name) => {
    if (name.innerText.toLowerCase().includes(chnlName)) {
      channel_list.insertAdjacentElement(
        "afterbegin",
        name.parentElement.parentElement.parentElement
      );
    }
  });
}
function show(side) {
  if (side === "chatside") {
    if (chatside.style.display === "none") {
      userside.style.display = "none";
      chatside.style.display = "block";
      // back.style.display = "block";
    }
  } else {
    if (userside.style.display === "none") {
      chatside.style.display = "none";
      userside.style.display = "block";
      // back.style.display = "none";
      chatbox.innerHTML = "";
      if (document.getElementsByClassName("active").length != 0) {
        document.getElementsByClassName("active")[0].classList.remove("active");
      }
    }
  }
}
function emphasize() {
  show("chatside");
}
function goto(This) {
  const to = This.classList[0].split("-");
  This = This.firstElementChild;
  let active = document.getElementsByClassName("active");
  if (active.length) {
    if (active[0] != This) {
      active[0].classList.remove("active");
    } else {
      return;
    }
  }
  This.classList.add("active");
  topic.innerText = This.innerText.split("\n")[0];
  emphasize();
  B4Change(This);
  // socket.emit("change", { Frnd: to[1] });
  if (to[0] == "c") {
    const server = localStorage.getItem("server");
    localStorage.setItem("channel", to[1]);
    getMessages(server, to[1]);
  }
}
function B4Change(to) {
  if (to.childElementCount == 3) {
    to.children[2].remove();
  }
  chatbox.innerHTML = "";
  message_input.value = "";
  // if (listblock.style.display == "block") {
  //   const clickEvent = new Event("click");
  //   Users.  chEvent(clickEvent);
  // }
  // if (pins.style.display == "block") {
  //   const clickEvent = new Event("click");
  //   attachment.dispatchEvent(clickEvent);
  // }
  // if (emojiPallet.style.display == "block") {
  //   const clickEvent = new Event("click");
  //   emoji_btn.dispatchEvent(clickEvent);
  // }
}
makeHoverable(attachment, pins);
makeHoverable(Users, listblock);
makeHoverable(emoji_btn, emojiPallet);
makeHoverable(threeDot, options);
function ready4change(Newserver) {
  if (localStorage.getItem("server") != Newserver.firstElementChild.innerText) {
    B4Change(Newserver);
    mediaPool.innerHTML = "";
    Newserver = Newserver.innerText;
    gotoserver(Newserver);
  }
}
function gotoserver(Newserver) {
  server.innerText = Newserver;
  // if (Newserver != "app") {
    // download.href = "/download/" + Newserver;
    // download.style.visibility = "visible";
  // } else {
    // download.href = "#";
    // download.style.visibility = "hidden";
  // }
  localStorage.setItem("server", Newserver);
  show("userside");
  channel_list.innerHTML = "";
  getChannels(Newserver);
  getMedia(Newserver);
  userCount.innerText = "0";
  userList.innerHTML = "";
  getPeople(Newserver);
}
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
function addmedia(data) {
  //data = [id,hash,name]
  const mediaplate = document.createElement("div");
  const nameplate = document.createElement("div");
  nameplate.classList.add("pinned");
  const name = data.name; //name=[name,mime]
  nameplate.innerText = name;
  nameplate.setAttribute(
    "onclick",
    "showpinned('" +
      data.mdid +
      "','" +
      data.hash +
      "'" +
      ",'" +
      data.name +
      "','" +
      data.mime +
      "')"
  );
  const forward = document.createElement("div");
  forward.classList.add("forward");
  forward.style.display = "none";
  forward.setAttribute(
    "onclick",
    'reply("' + true + '","' + data.mdid + '","' + name + '")'
  );
  mediaplate.classList.add("mediatitle");
  mediaplate.appendChild(nameplate);
  mediaplate.appendChild(forward);
  mediaplate.classList.add("M-" + data.mdid);
  mediaplate.addEventListener("mouseenter", () => {
    forward.style.display = "block";
  });
  mediaplate.addEventListener("mouseleave", () => {
    forward.style.display = "none";
  });
  mediaPool.appendChild(mediaplate);
}
function addserver(data) {
  if (document.getElementsByClassName("s-" + data).length == 0) {
    const maindiv = document.createElement("div");
    maindiv.classList.add("text-block");
    maindiv.classList.add("s-" + data);
    const childdiv = document.createElement("div");
    const child1div = document.createElement("div");
    const child2div = document.createElement("div");
    const name = document.createElement("div");
    name.classList.add("SERVER");
    name.innerText = data;
    child1div.appendChild(name);
    childdiv.appendChild(child1div);
    childdiv.appendChild(child2div);
    maindiv.appendChild(childdiv);
    maindiv.setAttribute("onclick", "ready4change(this.firstElementChild)");
    servers.appendChild(maindiv);
  }
}
function makeFrnd(name) {
  var Frnd = document.createElement("div");
  Frnd.classList.add("message");
  Frnd.classList.add("frnd");
  Frnd.innerHTML = "<p onclick = GOTOfrnd('" + name + "')></p>";
  var frndname = document.createElement("div");
  frndname.innerText = name;
  Frnd.firstChild.appendChild(frndname);
  return Frnd;
}
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
  const server = localStorage.getItem("server");
  const channel = localStorage.getItem("channel");
  socket.emit("reaction", [server, channel, id, emoji]);
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
function reply(media = false, id, content = null) {
  if (chatinput.childElementCount == 1) {
    const plate = document.createElement("div");
    plate.classList.add("replydiv");
    box.style.height = "70vh";
    if (!media) {
      if (!content) {
        content = document.getElementsByClassName("m-" + id)[0].children[1]
          .innerText;
      }
      plate.innerHTML =
        '<p class="replyplate repmsg"><small> "Reply:\n</small>' +
        content +
        '</p><button class="replydelete" onclick="removereply()">X</button>';
      reply_id.value = id;
    } else {
      plate.innerHTML =
        '<p class="replyplate repMd"><small>Attachment:\n' +
        content +
        '</small></p><button class="replydelete" onclick="removeattach()">X</button>';
      media_id.value = id;
    }
    chatinput.insertAdjacentElement("afterbegin", plate);
  } else {
    if (media == null) {
      if (!content) {
        content = document.getElementsByClassName("m-" + id)[0].children[1]
          .innerText;
      }
      reply_id.value = id;
      const repmsg = document.getElementsByClassName("repmsg")[0];
      if (repmsg) {
        repmsg.innerText = "Reply:\n" + content;
      } else {
        removeattach();
        reply(media, id, content);
      }
    } else {
      media_id.value = id;
      const repMd = document.getElementsByClassName("repMd")[0];
      if (repMd) {
        repMd.innerText = "Attach:\n" + content;
      } else {
        removereply();
        reply(media, id, content);
      }
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
        if (event.target != emoji_btn) {
          document.removeEventListener("click", e);

          message.lastElementChild.remove();
          if (!message.contains(event.target)) {
            message.lastChild.style.display = "none";
          }
          if (event.target.classList.contains("emoG")) {
            event.stopPropagation();
            react(
              event.target.innerText,
              message.firstChild.classList[0].split("-")[1]
            );
            message_input.value = message_input.value.slice(
              0,
              message_input.value.length - 3
            );
          }
        }
      }
      if (done && event.target == message.children[1]) {
        done = false;
      }
    });
  }
}
function GOTOfrnd(user, GOTO = true) {
  console.log("DM's are not included in this version");
  // const frnd = document.getElementsByClassName("f-" + user)[0];
  // if (!frnd) {
  //   const friend = document.createElement("div");
  //   friend.classList.add("f-" + user);
  //   friend.setAttribute("onclick", "goto(this)");
  //   const block = document.createElement("div");
  //   block.classList.add("block");
  //   block.innerHTML =
  //     '<div class="imgbx"><img src="/static/person.png" alt="pic" class="cover"></div><div class="details"><div class="name">' +
  //     user +
  //     "</div></div>";
  //   friend.appendChild(block);
  //   const isActive = document.getElementsByClassName("active")[0];
  //   if (isActive && isActive.parentElement == channel_list.firstElementChild) {
  //     channel_list.insertBefore(
  //       friend,
  //       isActive.parentElement.nextElementSibling
  //     );
  //   } else {
  //     channel_list.insertAdjacentElement("afterbegin", friend);
  //     friend.scrollIntoView();
  //   }
  //   if (GOTO) {
  //     goto(friend);
  //   }
  // }
  // if (GOTO) {
  //   goto(frnd);
  // }
}
function shownotification(to, name) {
  const Notify = document.getElementsByClassName(to + name);
  if (Notify.length) {
    const notify = Notify[0].firstElementChild;
    if (notify.childElementCount != 3) {
      let num = document.createElement("p");
      num.classList.add("update");
      num.innerText = "1";
      notify.appendChild(num);
    } else {
      let num = parseInt(notify.children[2].innerText);
      notify.children[2].innerText = num + 1;
    }
    if (to != "s-") {
      const isActive = document.getElementsByClassName("active")[0];
      if (
        isActive &&
        isActive.parentElement == channel_list.firstElementChild
      ) {
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
function showUser(name) {
  if (!document.getElementsByClassName("U-" + name).length) {
    let live = parseInt(userCount.innerText);
    if (!live) {
      live = 0;
    }
    userCount.innerText = live + 1;
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
search_form.onsubmit = function () {
  if (options.style.display == "block") {
    const clickEvent = new Event("click");
    threeDot.dispatchEvent(clickEvent);
  }
  const chnlName = search_input.value.trim();
  if (chnlName.length != 0) {
    search_input.value = "";
    if (search_form.dataset.create == "y") {
      search_input.placeholder = "Search Channel";
      search_form.setAttribute("data-create", "n");
      search_input.style.border = "none";
      socket.emit("create", [localStorage.getItem("server"), chnlName]);
    } else {
      rearrange(chnlName);
      channel_list.scrollTop = "";
    }
  }
  return false;
};
message_form.onsubmit = function () {
  let message = message_input.value.trim();
  if (!message.length) {
    if (!media_id.value) {
      return false;
    }
  }
  const server = localStorage.getItem("server");
  const channel = localStorage.getItem("channel");
  if (!server || !channel) {
    return;
  }
  let msg = { msgData: message, server: server, channel: channel };
  if (media_id.value || reply_id.value) {
    document.getElementsByClassName("replydiv")[0].remove();
    box.style.height = "74vh";
  }
  if (reply_id.value) {
    msg["replyId"] = reply_id.value;
    reply_id.value = "";
  }
  if (media_id.value) {
    msg["mediaId"] = media_id.value;
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
function showing(data, top) {
  const channel = document.createElement("div");
  channel.setAttribute("onclick", "goto(this)");
  channel.classList.add("c-" + data.cid);
  const block = document.createElement("div");
  block.classList.add("block");
  block.innerHTML =
    '<div class="imgbx"><img src="/static/profile.webp" alt="pic" class="cover"></div><div class="details"><div class="name">' +
    data.name +
    '</h4></div><div class="creator"><p>created by ' +
    data.creator +
    '</p><!-- <b onclick="location.href="/delete">x</b> --></div></div>';
  channel.appendChild(block);
  if (top) {
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
  } else {
    channel_list.appendChild(channel);
  }
}
function showinfo(ch){
  // Info.innerHTML=""
}
localStorage.clear();

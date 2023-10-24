const key = self.crypto.subtle.generateKey(
  {
    name: "RSA-OAEP",
    modulusLength: 2048,
    publicExponent: new Uint8Array([0x01, 0x00, 0x01]),
    hash: "SHA-256",
  },
  false,
  ["encrypt", "decrypt"]
);
const pubKeys = {};
onmessage = async function (e) {
  const data = e.data;
  const opr = data.operation;
  if (opr == 0) {
    //export the pub key
    const publicKey = await crypto.subtle.exportKey(
      "jwk",
      (
        await key
      ).publicKey
    );
    console.log("keys generated");
    self.postMessage({ operation: 0, key: publicKey });
  } else if (opr == 1) {
    //import the pub key
    const publicKey = await crypto.subtle.importKey(
      "jwk",
      {
        kty: "RSA",
        n: data.key,
        e: "AQAB",
        ext: true,
        key_ops: ["encrypt"],
      },
      { name: "RSA-OAEP", hash: "SHA-256" },
      true,
      ["encrypt"]
    );
    pubKeys[data.server + data.id] = publicKey;
    console.log("pub key set for " + data.server + data.id);
  } else if (opr == 2) {
    if (data.server + data.id in pubKeys) {
      // encrypt using the publicKey by updating the msg key
      const msgbuffer = new TextEncoder().encode(data.msg);
      const encmsgbuffer = await crypto.subtle.encrypt(
        { name: "RSA-OAEP" },
        pubKeys[data.server + data.id],
        msgbuffer
      );
      data.msg = btoa(String.fromCharCode(...new Uint8Array(encmsgbuffer)));
      self.postMessage(data);
    } else {
      self.postMessage(data);
    }
  } else if (opr == 3) {
    const encmsgbuffer = new Uint8Array(atob(data.msg).split('').map(c => c.charCodeAt(0)));
    const dcrptmsgbuffer = await crypto.subtle.decrypt(
      { name: "RSA-OAEP" },
      (
        await key
      ).privateKey,
      encmsgbuffer
    );
    data.msg = new TextDecoder().decode(dcrptmsgbuffer);
    self.postMessage(data);
  }
}
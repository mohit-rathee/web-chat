const key = self.crypto.subtle.generateKey(
    {
      name: "RSA-OAEP",
      modulusLength: 2048,
      publicExponent: new Uint8Array([0x01, 0x00, 0x01]),
      hash: "SHA-256",
    },
    true,
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
    }
  };
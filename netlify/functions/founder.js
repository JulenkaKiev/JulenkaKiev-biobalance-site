const { getStore, connectLambda } = require("@netlify/blobs");

const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || "biobalance2026";
const MAX_PHOTO_BYTES = 4 * 1024 * 1024;
const KEY = "main";

exports.handler = async (event) => {
  connectLambda(event);
  const store = getStore("founder-photo");

  if (event.httpMethod === "OPTIONS") {
    return {
      statusCode: 204,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
      },
      body: "",
    };
  }

  if (event.httpMethod === "GET") {
    const result = await store.getWithMetadata(KEY, { type: "arrayBuffer" });
    if (!result) {
      return { statusCode: 404, body: "Not found" };
    }
    const contentType = (result.metadata && result.metadata.contentType) || "image/jpeg";
    return {
      statusCode: 200,
      headers: {
        "Content-Type": contentType,
        "Cache-Control": "public, max-age=300",
      },
      body: Buffer.from(result.data).toString("base64"),
      isBase64Encoded: true,
    };
  }

  if (event.httpMethod === "POST") {
    let payload;
    try {
      payload = JSON.parse(event.body || "{}");
    } catch {
      return { statusCode: 400, headers: { "Content-Type": "application/json" }, body: JSON.stringify({ error: "Bad JSON" }) };
    }

    if (payload.password !== ADMIN_PASSWORD) {
      return { statusCode: 401, headers: { "Content-Type": "application/json" }, body: JSON.stringify({ error: "Невірний пароль" }) };
    }

    if (!payload.photoBase64) {
      return { statusCode: 400, headers: { "Content-Type": "application/json" }, body: JSON.stringify({ error: "Немає фото" }) };
    }

    const buffer = Buffer.from(payload.photoBase64, "base64");
    if (buffer.length > MAX_PHOTO_BYTES) {
      return { statusCode: 400, headers: { "Content-Type": "application/json" }, body: JSON.stringify({ error: "Фото занадто велике" }) };
    }

    await store.set(KEY, buffer, {
      metadata: { contentType: payload.photoType || "image/jpeg" },
    });

    return {
      statusCode: 200,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
      body: JSON.stringify({ ok: true }),
    };
  }

  return { statusCode: 405, body: "Method not allowed" };
};

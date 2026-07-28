const { getStore, connectLambda } = require("@netlify/blobs");

const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || "biobalance2026";
const MAX_PHOTO_BYTES = 4 * 1024 * 1024; // 4MB safety cap

function json(status, body) {
  return {
    statusCode: status,
    headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
    body: JSON.stringify(body),
  };
}

exports.handler = async (event) => {
  connectLambda(event);
  const dataStore = getStore("testimonials-data");
  const photoStore = getStore("testimonial-photos");

  if (event.httpMethod === "OPTIONS") {
    return {
      statusCode: 204,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
      },
      body: "",
    };
  }

  if (event.httpMethod === "GET") {
    const list = (await dataStore.get("list", { type: "json" })) || [];
    return json(200, { testimonials: list });
  }

  if (event.httpMethod === "POST") {
    let payload;
    try {
      payload = JSON.parse(event.body || "{}");
    } catch {
      return json(400, { error: "Bad JSON" });
    }

    if (payload.password !== ADMIN_PASSWORD) {
      return json(401, { error: "Невірний пароль" });
    }

    const name = (payload.name || "").trim().slice(0, 80);
    const quote = (payload.quote || "").trim().slice(0, 500);
    if (!name || !quote) {
      return json(400, { error: "Заповніть ім'я та текст відгуку" });
    }

    let photoId = null;
    if (payload.photoBase64) {
      const buffer = Buffer.from(payload.photoBase64, "base64");
      if (buffer.length > MAX_PHOTO_BYTES) {
        return json(400, { error: "Фото занадто велике" });
      }
      photoId = `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
      await photoStore.set(photoId, buffer, {
        metadata: { contentType: payload.photoType || "image/jpeg" },
      });
    }

    const list = (await dataStore.get("list", { type: "json" })) || [];
    const entry = {
      id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
      name,
      quote,
      photoId,
      createdAt: new Date().toISOString(),
    };
    list.unshift(entry);
    await dataStore.setJSON("list", list);

    return json(200, { ok: true, entry });
  }

  if (event.httpMethod === "DELETE") {
    let payload;
    try {
      payload = JSON.parse(event.body || "{}");
    } catch {
      return json(400, { error: "Bad JSON" });
    }
    if (payload.password !== ADMIN_PASSWORD) {
      return json(401, { error: "Невірний пароль" });
    }
    const list = (await dataStore.get("list", { type: "json" })) || [];
    const target = list.find((t) => t.id === payload.id);
    const next = list.filter((t) => t.id !== payload.id);
    await dataStore.setJSON("list", next);
    if (target && target.photoId) {
      await photoStore.delete(target.photoId);
    }
    return json(200, { ok: true });
  }

  return json(405, { error: "Method not allowed" });
};

const { getStore, connectLambda } = require("@netlify/blobs");

exports.handler = async (event) => {
  const id = event.queryStringParameters && event.queryStringParameters.id;
  if (!id) {
    return { statusCode: 400, body: "Missing id" };
  }

  connectLambda(event);
  const photoStore = getStore("testimonial-photos");
  const result = await photoStore.getWithMetadata(id, { type: "arrayBuffer" });

  if (!result) {
    return { statusCode: 404, body: "Not found" };
  }

  const contentType = (result.metadata && result.metadata.contentType) || "image/jpeg";
  return {
    statusCode: 200,
    headers: {
      "Content-Type": contentType,
      "Cache-Control": "public, max-age=31536000, immutable",
    },
    body: Buffer.from(result.data).toString("base64"),
    isBase64Encoded: true,
  };
};

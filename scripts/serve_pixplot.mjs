#!/usr/bin/env node
import { createServer } from "node:http";
import { readFile } from "node:fs/promises";
import { extname, join, resolve } from "node:path";

const port = Number(process.argv[2] || 8771);
const root = resolve(process.cwd());

const contentTypes = {
  ".css": "text/css",
  ".html": "text/html",
  ".ico": "image/x-icon",
  ".jpeg": "image/jpeg",
  ".jpg": "image/jpeg",
  ".js": "text/javascript",
  ".json": "application/json",
  ".png": "image/png",
  ".svg": "image/svg+xml",
};

function safePath(urlPath) {
  const decoded = decodeURIComponent(urlPath.split("?")[0]);
  const normalized = decoded.endsWith("/") ? `${decoded}index.html` : decoded;
  const filePath = resolve(join(root, normalized));
  return filePath.startsWith(root) ? filePath : null;
}

const server = createServer(async (request, response) => {
  const filePath = safePath(request.url || "/");
  if (!filePath) {
    response.writeHead(403, { "content-length": 9 });
    response.end("forbidden");
    return;
  }

  try {
    const body = await readFile(filePath);
    response.writeHead(200, {
      "content-length": body.length,
      "content-type": contentTypes[extname(filePath).toLowerCase()] || "application/octet-stream",
    });
    response.end(body);
  } catch {
    response.writeHead(404, { "content-length": 9 });
    response.end("not found");
  }
});

server.listen(port, "127.0.0.1", () => {
  console.log(`PixPlot preview: http://127.0.0.1:${port}/data/pixplot/met-cloud-200/`);
});

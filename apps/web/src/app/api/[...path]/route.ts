import type { NextRequest } from "next/server";

async function forward(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> },
) {
  const { path } = await context.params;
  if (
    path[0] !== "v1" ||
    path.some((part) => !/^[A-Za-z0-9_.-]+$/.test(part) || part === "..")
  )
    return new Response(null, { status: 404 });
  const headers = new Headers();
  for (const key of [
    "content-type",
    "cookie",
    "authorization",
    "origin",
    "x-csrf-token",
    "x-razorpay-signature",
    "x-razorpay-event-id",
    "x-hub-signature-256",
  ]) {
    const value = request.headers.get(key);
    if (value) headers.set(key, value);
  }
  const limit = path.join("/") === "v1/admin/media" ? 5_000_000 : 1_000_000;
  const chunks: Uint8Array[] = [];
  let length = 0;
  if (request.body) {
    const reader = request.body.getReader();
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;
      length += value.length;
      if (length > limit) {
        await reader.cancel();
        return Response.json(
          { detail: "Request is too large" },
          { status: 413 },
        );
      }
      chunks.push(value);
    }
  }
  const body = new Uint8Array(length);
  let offset = 0;
  for (const chunk of chunks) {
    body.set(chunk, offset);
    offset += chunk.length;
  }
  try {
    const response = await fetch(
      `${process.env.CONTENT_API_URL ?? "http://127.0.0.1:8500"}/${path.join("/")}${request.nextUrl.search}`,
      {
        method: request.method,
        headers,
        body: ["GET", "HEAD"].includes(request.method) ? undefined : body,
        redirect: "manual",
        cache: "no-store",
        signal: AbortSignal.timeout(20000),
      },
    );
    const output = new Headers({
      "Cache-Control": "private, no-store",
      "X-Robots-Tag": "noindex, nofollow",
      "Referrer-Policy": "no-referrer",
      "X-Content-Type-Options": "nosniff",
    });
    for (const key of ["content-type", "content-disposition"]) {
      const value = response.headers.get(key);
      if (value) output.set(key, value);
    }
    for (const cookie of response.headers.getSetCookie())
      output.append("Set-Cookie", cookie);
    return new Response(response.body, {
      status: response.status,
      headers: output,
    });
  } catch {
    return Response.json(
      { detail: "The service is temporarily unavailable. Please try again." },
      { status: 503 },
    );
  }
}
export const GET = forward;
export const POST = forward;
export const PUT = forward;

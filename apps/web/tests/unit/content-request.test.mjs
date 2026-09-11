import test from "node:test";
import assert from "node:assert/strict";
import { fetchStorefront } from "../../src/lib/content-request.mjs";

test("a transient content timeout retries a fresh uncached snapshot", async () => {
  let calls = 0;
  const signals = [];
  const result = await fetchStorefront(
    "http://content.fixture",
    async (url, options) => {
      assert.equal(url, "http://content.fixture/v1/storefront");
      assert.equal(options.cache, "no-store");
      signals.push(options.signal);
      if (++calls === 1)
        throw new DOMException("Read timed out", "TimeoutError");
      return Response.json({ revision: "new", products: [] });
    },
  );
  assert.deepEqual(result, { revision: "new", products: [] });
  assert.equal(calls, 2);
  assert.notEqual(signals[0], signals[1]);
});

test("persistent transport failure stays visible after one retry", async () => {
  let calls = 0;
  await assert.rejects(
    fetchStorefront("http://content.fixture", async () => {
      calls++;
      throw new TypeError("fetch failed");
    }),
    /fetch failed/,
  );
  assert.equal(calls, 2);
});

test("an upstream refusal is not retried or replaced with cached content", async () => {
  let calls = 0;
  await assert.rejects(
    fetchStorefront("http://content.fixture", async () => {
      calls++;
      return new Response("Unavailable", { status: 503 });
    }),
    /temporarily unavailable/,
  );
  assert.equal(calls, 1);
});

test("malformed content is rejected without a transport retry", async () => {
  let calls = 0;
  await assert.rejects(
    fetchStorefront("http://content.fixture", async () => {
      calls++;
      return new Response("invalid JSON", { status: 200 });
    }),
    SyntaxError,
  );
  assert.equal(calls, 1);
});

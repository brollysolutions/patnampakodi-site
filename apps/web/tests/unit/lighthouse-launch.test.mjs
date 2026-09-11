import assert from "node:assert/strict";
import test from "node:test";
import { Launcher } from "chrome-launcher";
import { lighthouseChromeArgs } from "../../scripts/lighthouse-launch.mjs";

test("Lighthouse launch retains tool defaults and the Linux SUID sandbox", () => {
  const original = Object.getOwnPropertyDescriptor(process, "platform");
  Object.defineProperty(process, "platform", { value: "linux" });
  try {
    assert.ok(new Launcher().flags.includes("--disable-setuid-sandbox"));
    const args = lighthouseChromeArgs(new URL("https://localhost:3510"));
    const flags = args[1].slice("--chrome-flags=".length).split(" ");
    const actual = new Launcher({
      ignoreDefaultFlags: args.includes("--chrome-ignore-default-flags"),
      chromeFlags: flags,
    }).flags;
    assert.ok(!actual.includes("--disable-setuid-sandbox"));
    assert.ok(!actual.includes("--no-sandbox"));
    for (const flag of Launcher.defaultFlags())
      assert.ok(actual.includes(flag));
    assert.ok(actual.includes("--headless"));
    assert.ok(actual.includes("--allow-insecure-localhost"));
    assert.ok(
      !lighthouseChromeArgs(new URL("http://127.0.0.1:3510"))[1].includes(
        "--allow-insecure-localhost",
      ),
    );
  } finally {
    Object.defineProperty(process, "platform", original);
  }
});

import { access, mkdir, stat, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { spawn } from "node:child_process";
import { chromium } from "@playwright/test";
import { passesBudgets, summarizeRuns } from "./performance-policy.mjs";
import { lighthouseChromeArgs } from "./lighthouse-launch.mjs";

const chromePath = chromium.executablePath();
await access(chromePath);

// CI's Ubuntu AppArmor policy blocks the downloaded browser's user namespaces.
// CI installs the pinned browser's companion helper with the required ownership.
if (process.env.CHROME_DEVEL_SANDBOX) {
  const helper = await stat(process.env.CHROME_DEVEL_SANDBOX);
  if (!helper.isFile() || helper.uid !== 0 || (helper.mode & 0o7777) !== 0o4755)
    throw new Error(
      `Chrome sandbox helper must be root-owned mode 4755 (uid=${helper.uid}, mode=${(helper.mode & 0o7777).toString(8)})`,
    );
}

const directory = resolve(
  "../../.agent-workflow/reports",
  `lighthouse-${Date.now()}`,
);
await mkdir(directory, { recursive: true });
const results = [];
const baseURL = new URL(
  process.env.LIGHTHOUSE_BASE_URL ?? "http://127.0.0.1:3010",
);
if (!["127.0.0.1", "localhost", "[::1]"].includes(baseURL.hostname))
  throw new Error("Performance verification requires a local fixture URL");
for (const route of ["/", "/menu/", "/contact/"]) {
  for (const device of ["mobile", "desktop"]) {
    for (let attempt = 1; attempt <= 3; attempt++) {
      const file = resolve(
        directory,
        `${route.replaceAll("/", "") || "home"}-${device}-${attempt}`,
      );
      const args = [
        "node_modules/lighthouse/cli/index.js",
        new URL(route, baseURL).href,
        "--save-assets",
        "--output=json",
        "--output=html",
        `--output-path=${file}`,
        ...lighthouseChromeArgs(baseURL),
        "--only-categories=performance,accessibility,best-practices,seo",
      ];
      if (device === "desktop") args.push("--preset=desktop");
      await new Promise((accept, reject) => {
        const child = spawn(process.execPath, args, {
          stdio: "inherit",
          windowsHide: true,
          env: { ...process.env, CHROME_PATH: chromePath },
        });
        child.on("error", reject);
        child.on("exit", (code) =>
          code === 0
            ? accept()
            : reject(new Error(`Lighthouse exited ${code}`)),
        );
      });
      const { readFile } = await import("node:fs/promises");
      const report = JSON.parse(await readFile(`${file}.report.json`, "utf8"));
      if (report.runtimeError)
        throw new Error(JSON.stringify(report.runtimeError));
      const scores = Object.fromEntries(
        Object.entries(report.categories).map(([key, value]) => [
          key,
          value.score,
        ]),
      );
      const metrics = Object.fromEntries(
        [
          "largest-contentful-paint",
          "cumulative-layout-shift",
          "total-blocking-time",
        ].map((key) => [key, report.audits[key].numericValue]),
      );
      const passed = passesBudgets(scores, metrics);
      const result = {
        route,
        device,
        attempt,
        passed,
        scores,
        metrics,
        browser: report.environment.hostUserAgent,
        benchmarkIndex: report.environment.benchmarkIndex,
        lighthouseVersion: report.lighthouseVersion,
        warnings: report.runWarnings,
        report: file,
      };
      results.push(result);
      console.log(JSON.stringify(result));
      if (!passed)
        console.log(
          JSON.stringify({
            route,
            device,
            attempt,
            diagnostics: Object.fromEntries(
              ["mainthread-work-breakdown", "bootup-time", "long-tasks"].map(
                (key) => [key, report.audits[key]?.details?.items ?? []],
              ),
            ),
          }),
        );
    }
  }
}
// Three sequential cold-browser runs reduce host scheduling noise. Preserve every
// observation; correctness categories must pass every time, performance uses medians.
const summaries = [];
for (const route of ["/", "/menu/", "/contact/"]) {
  for (const device of ["mobile", "desktop"]) {
    summaries.push(
      summarizeRuns(
        results.filter(
          (result) => result.route === route && result.device === device,
        ),
      ),
    );
  }
}
await writeFile(
  resolve(directory, "summary.json"),
  JSON.stringify({ runs: results, medians: summaries }, null, 2),
);
console.log(JSON.stringify({ medians: summaries }));
if (summaries.some((result) => !result.passed)) process.exitCode = 1;

import assert from "node:assert/strict";
import test from "node:test";
import {
  passesBudgets,
  summarizeRuns,
} from "../../scripts/performance-policy.mjs";

const sample = (blocking = 100) => ({
  route: "/",
  device: "mobile",
  scores: { performance: 0.98, accessibility: 1, "best-practices": 1, seo: 1 },
  metrics: {
    "largest-contentful-paint": 2000,
    "cumulative-layout-shift": 0,
    "total-blocking-time": blocking,
  },
});

test("a scheduling outlier remains visible while repeated slow runs fail", () => {
  const result = summarizeRuns([sample(), sample(500), sample(90)]);
  assert.equal(result.passed, true);
  assert.equal(result.individualFailures, 1);
  assert.equal(result.metrics["total-blocking-time"], 100);
  assert.equal(
    summarizeRuns([sample(), sample(500), sample(300)]).passed,
    false,
  );
});

test("median performance never hides a failed accessibility or SEO run", () => {
  for (const category of ["accessibility", "seo", "best-practices"]) {
    const failed = sample();
    failed.scores[category] = 0.8;
    assert.equal(summarizeRuns([sample(), failed, sample()]).passed, false);
  }
});

test("invalid or incomplete observations cannot pass", () => {
  const missing = sample();
  missing.metrics["total-blocking-time"] = null;
  assert.equal(passesBudgets(missing.scores, missing.metrics), false);
  assert.equal(summarizeRuns([sample(), sample(), missing]).passed, false);
  assert.throws(() => summarizeRuns([sample(), sample()]));
  assert.throws(() =>
    summarizeRuns([sample(), sample(), { ...sample(), device: "desktop" }]),
  );
});

test("render, layout-shift and performance-score budgets stay enforced", () => {
  for (const [key, value] of [
    ["largest-contentful-paint", 2501],
    ["cumulative-layout-shift", 0.11],
  ]) {
    const slow = sample();
    slow.metrics[key] = value;
    assert.equal(summarizeRuns([sample(), slow, slow]).passed, false);
  }
  const slow = sample();
  slow.scores.performance = 0.89;
  assert.equal(summarizeRuns([sample(), slow, slow]).passed, false);
});

const metricNames = [
  "largest-contentful-paint",
  "cumulative-layout-shift",
  "total-blocking-time",
];

const complete = ({ scores, metrics }) =>
  ["performance", "accessibility", "best-practices", "seo"].every((key) =>
    Number.isFinite(scores[key]),
  ) && metricNames.every((key) => Number.isFinite(metrics[key]));

export function passesBudgets(scores, metrics) {
  return (
    complete({ scores, metrics }) &&
    scores.performance >= 0.9 &&
    scores.accessibility === 1 &&
    scores["best-practices"] >= 0.9 &&
    scores.seo === 1 &&
    metrics["largest-contentful-paint"] <= 2500 &&
    metrics["cumulative-layout-shift"] <= 0.1 &&
    metrics["total-blocking-time"] <= 200
  );
}

export function summarizeRuns(runs) {
  if (
    runs.length !== 3 ||
    runs.some(
      (run) => run.route !== runs[0].route || run.device !== runs[0].device,
    )
  )
    throw new Error("Expected three runs of the same route and device");
  const median = (values) => [...values].sort((a, b) => a - b)[1];
  const metrics = Object.fromEntries(
    metricNames.map((key) => [
      key,
      median(runs.map((run) => run.metrics[key])),
    ]),
  );
  const scores = {
    performance: median(runs.map((run) => run.scores.performance)),
    ...Object.fromEntries(
      ["accessibility", "best-practices", "seo"].map((key) => [
        key,
        Math.min(...runs.map((run) => run.scores[key])),
      ]),
    ),
  };
  return {
    route: runs[0].route,
    device: runs[0].device,
    passed: runs.every(complete) && passesBudgets(scores, metrics),
    scores,
    metrics,
    individualFailures: runs.filter(
      (run) => !passesBudgets(run.scores, run.metrics),
    ).length,
  };
}

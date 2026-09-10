export async function AnalyticsGate() {
  const measurementId = process.env.GA4_MEASUREMENT_ID ?? "";
  if (!/^G-[A-Z0-9]+$/.test(measurementId)) return null;
  const { Analytics } = await import("./Analytics");
  return <Analytics measurementId={measurementId} />;
}

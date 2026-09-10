import { Launcher } from "chrome-launcher";

export function lighthouseChromeArgs(baseURL) {
  // Preserve the pinned launcher's defaults without its implicit Linux
  // --disable-setuid-sandbox addition, which defeats CHROME_DEVEL_SANDBOX.
  const flags = Launcher.defaultFlags();
  if (
    flags.some((flag) =>
      /--(?:no-sandbox|disable-setuid-sandbox)(?:=|$)/.test(flag),
    )
  )
    throw Error("Lighthouse defaults must retain the browser sandbox");
  flags.push("--headless", "--disable-dev-shm-usage");
  if (baseURL.protocol === "https:") flags.push("--allow-insecure-localhost");
  return ["--chrome-ignore-default-flags", `--chrome-flags=${flags.join(" ")}`];
}

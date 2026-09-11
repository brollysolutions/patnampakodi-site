/** Fetch a fresh public snapshot, retrying one transient transport failure. */
export async function fetchStorefront(base, request = fetch) {
  let response;
  for (let attempt = 0; attempt < 2; attempt++) {
    try {
      response = await request(`${base}/v1/storefront`, {
        cache: "no-store",
        signal: AbortSignal.timeout(5000),
      });
      break;
    } catch (error) {
      const transient =
        error?.name === "TimeoutError" ||
        (error instanceof TypeError && error.message === "fetch failed");
      if (!transient || attempt === 1) throw error;
    }
  }
  if (!response?.ok)
    throw new Error(
      "The menu is temporarily unavailable. Please try again shortly.",
    );
  return response.json();
}

// src/lib/utils/fetchWithRateLimit.ts
import { rateLimitStore } from "$lib/store/rateLimitStore"; // ← cambia "stores" a "store"

export async function fetchWithRateLimit(
  input: RequestInfo | URL,
  init?: RequestInit,
): Promise<Response> {
  const response = await fetch(input, init);
  if (response.status === 429) {
    let message = "Has superado el límite de peticiones. Inténtalo más tarde.";
    let waitSeconds = 0;
    const clonedResponse = response.clone();
    try {
      const data = await clonedResponse.json();
      if (data.detail && typeof data.detail === "string") {
        message = data.detail;
        const match = data.detail.match(/Expected available in (\d+) seconds?/);
        if (match) waitSeconds = parseInt(match[1], 10);
      }
    } catch (e) {}
    if (!waitSeconds && response.headers.has("Retry-After")) {
      const retryAfter = response.headers.get("Retry-After");
      if (retryAfter && !isNaN(parseInt(retryAfter, 10)))
        waitSeconds = parseInt(retryAfter, 10);
    }
    rateLimitStore.show(message, waitSeconds);
    return response;
  }
  return response;
}

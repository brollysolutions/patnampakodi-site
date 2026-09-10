import { indexable, PRIVATE_PREFIXES } from "./src/lib/policy.mjs";
import { fileURLToPath } from "node:url";

const securityHeaders = [
  { key: "X-Content-Type-Options", value: "nosniff" },
  { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
  { key: "X-Frame-Options", value: "DENY" },
  {
    key: "Permissions-Policy",
    value: "camera=(), microphone=(), geolocation=()",
  },
  {
    key: "Content-Security-Policy",
    value:
      "default-src 'self'; script-src 'self' 'unsafe-inline' https://www.googletagmanager.com; style-src 'self' 'unsafe-inline'; img-src 'self' data: https://*.google-analytics.com; font-src 'self'; connect-src 'self' https://*.google-analytics.com; object-src 'none'; base-uri 'self'; frame-ancestors 'none'; form-action 'self'",
  },
];

const nextConfig = {
  output: "standalone",
  outputFileTracingRoot: fileURLToPath(new URL("../..", import.meta.url)),
  poweredByHeader: false,
  trailingSlash: true,
  typedRoutes: true,
  htmlLimitedBots: /.*/,
  images: {
    formats: ["image/avif", "image/webp"],
    qualities: [45, 75],
    remotePatterns: [],
  },
  async headers() {
    const robots = { key: "X-Robots-Tag", value: "noindex, nofollow" };
    return [
      {
        source: "/:path*",
        headers: [
          ...securityHeaders,
          ...(indexable(process.env) ? [] : [robots]),
        ],
      },
      ...PRIVATE_PREFIXES.map((prefix) => ({
        source: `/${prefix}/:path*`,
        headers: [robots, { key: "Cache-Control", value: "private, no-store" }],
      })),
    ];
  },
};

export default nextConfig;

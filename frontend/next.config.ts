import type { NextConfig } from "next";

// Where the FastAPI backend lives. Inside Docker Compose it's the "backend" service.
const backendUrl = process.env.BACKEND_URL ?? "http://localhost:8000";

const nextConfig: NextConfig = {
  // Proxy /api/* to FastAPI so the browser only ever talks to this app
  // (same origin: no CORS setup needed, and the backend stays internal).
  async rewrites() {
    return [{ source: "/api/:path*", destination: `${backendUrl}/api/:path*` }];
  },
};

export default nextConfig;

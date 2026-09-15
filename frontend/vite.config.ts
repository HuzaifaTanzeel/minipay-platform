import path from "node:path";
import react from "@vitejs/plugin-react";
import { defineConfig, loadEnv } from "vite";

// The API key is read from the server-side Vite env (frontend/.env) and
// injected into proxied /api requests here. It is NOT exposed to the browser
// bundle (we intentionally do not prefix it with VITE_).
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const apiTarget = env.API_PROXY_TARGET || "http://localhost:8000";
  const apiKey = env.API_KEY || "";

  return {
    plugins: [react()],
    resolve: {
      alias: { "@": path.resolve(__dirname, "./src") },
    },
    server: {
      port: 5173,
      proxy: {
        "/api": {
          target: apiTarget,
          changeOrigin: true,
          configure: (proxy) => {
            proxy.on("proxyReq", (proxyReq) => {
              if (apiKey) proxyReq.setHeader("X-API-Key", apiKey);
            });
          },
        },
      },
    },
  };
});

import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import svgr from "vite-plugin-svgr";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const appBase = env.VITE_APP_BASE || "/";
  const normalizedBase = appBase.endsWith("/") ? appBase : `${appBase}/`;

  return {
    base: normalizedBase,

    plugins: [react(), svgr()],

    server: {
      host: true,
      hmr: {
        protocol: "wss",
      },
    },
  };
});
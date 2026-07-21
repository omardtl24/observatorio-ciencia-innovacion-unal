import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import svgr from "vite-plugin-svgr";

export default defineConfig({
  base: env.VITE_APP_BASE || "/",

  plugins: [
    react(),
    svgr(),
  ],

  server: {
    host: true,
    hmr: {
      protocol: "wss",
    },
  },
});
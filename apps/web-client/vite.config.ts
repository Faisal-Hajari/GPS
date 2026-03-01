import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@gps/ui-components": path.resolve(__dirname, "../../packages/ui-components/src"),
    },
  },
  envDir: ".",
  server: {
    proxy: {
      "/stac": { target: "http://127.0.0.1:8000", changeOrigin: true },
      "/cog":  { target: "http://127.0.0.1:8000", changeOrigin: true },
    },
  },
});
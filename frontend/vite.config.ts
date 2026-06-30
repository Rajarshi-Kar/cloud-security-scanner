import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    // Docker Desktop bind mounts on Windows don't reliably forward filesystem
    // change events into the container, so chokidar needs polling to notice edits.
    watch: {
      usePolling: true,
      interval: 300,
    },
    proxy: {
      "/api": {
        target: "http://backend:8000",
        changeOrigin: true,
      },
    },
  },
});

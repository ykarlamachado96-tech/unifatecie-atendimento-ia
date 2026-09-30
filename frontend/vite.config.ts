import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    // permite acesso via túnel público (trycloudflare.com muda de host a cada reinício)
    allowedHosts: true,
    watch: {
      usePolling: true,
      interval: 300,
    },
  },
});

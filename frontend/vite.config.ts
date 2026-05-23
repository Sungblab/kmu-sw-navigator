import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  build: {
    chunkSizeWarningLimit: 600,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (
            id.includes("node_modules/streamdown") ||
            id.includes("node_modules/@streamdown") ||
            id.includes("node_modules/shiki") ||
            id.includes("node_modules/hast-util")
          ) {
            return "streamdown";
          }
        },
      },
    },
  },
});

import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
<<<<<<< HEAD
  server: { port: 5174 },
=======
  server: {
    port: 5174,
    proxy: {
      "/api": "http://127.0.0.1:8420",
    },
  },
>>>>>>> 7cbc55677b79be1bd66e40b264776391f23037bb
});

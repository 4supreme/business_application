import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwind from "@tailwindcss/vite";   // ⬅️ добавили

export default defineConfig({
  plugins: [react(), tailwind()],           // ⬅️ добавили
});
import react from "@vitejs/plugin-react";
import { fileURLToPath } from "node:url";
import { defineConfig } from "vite";

const rootDirectory = fileURLToPath(new URL(".", import.meta.url));

export default defineConfig({
  plugins: [
    react(),
    {
      name: "monitoring-route",
      configureServer(server) {
        server.middlewares.use((request, _response, next) => {
          if (request.url === "/monitoring" || request.url?.startsWith("/monitoring?")) {
            request.url = "/monitoring.html";
          }
          next();
        });
      }
    }
  ],
  build: {
    rollupOptions: {
      input: {
        main: `${rootDirectory}index.html`,
        monitoring: `${rootDirectory}monitoring.html`
      }
    }
  }
});

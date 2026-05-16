import sitemap from "@astrojs/sitemap";
import { defineConfig } from "astro/config";

export default defineConfig({
  output: "static",
  trailingSlash: "always",
  site: "https://engebreth.com",
  integrations: [sitemap()],
});

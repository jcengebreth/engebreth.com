import { defineConfig } from "astro/config";

export default defineConfig({
  // Static output for S3 + CloudFront deployment
  output: "static",
  trailingSlash: "always",
});

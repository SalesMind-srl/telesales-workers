import { Hono } from "hono";
import { cors } from "hono/cors";
import type { Env } from "./types";
import { healthHandler } from "./handlers/health";
import { batchesHandler, processHandler } from "./handlers/batches";
import { statsHandler } from "./handlers/stats";
import { cronHandler } from "./handlers/cron";

const app = new Hono<{ Bindings: Env }>();

// Middleware
app.use("*", cors());

// Health check
app.get("/health", healthHandler);

// Batches
app.get("/batches", batchesHandler);
app.post("/process/:batch_id", processHandler);

// Stats
app.get("/stats", statsHandler);

// Cron (internal)
app.post("/internal/check", cronHandler);

// Fallback
app.all("*", (c) => {
  return c.json({ error: "Not Found" }, 404);
});

// Export for Cloudflare Workers
export default {
  fetch: app.fetch,
  async scheduled(event: ScheduledEvent, env: Env) {
    try {
      const result = await cronHandler({ env } as any);
      console.log("Cron executed:", result);
    } catch (error) {
      console.error("Cron error:", error);
    }
  },
};

// Export types
export type { Env };

import { Context } from "hono";
import type { Env, HealthStatus } from "../types";

export async function healthHandler(c: Context<{ Bindings: Env }>) {
  try {
    const env = c.env;

    // Check KV connectivity
    const lastCheck = await env.KV.get("last_check_timestamp");

    const status: HealthStatus = {
      status: "ok",
      scheduler_running: true,
      last_check: lastCheck || undefined,
      next_check: new Date(Date.now() + 5 * 60 * 1000).toISOString(),
    };

    return c.json(status, 200);
  } catch (error: any) {
    return c.json(
      {
        status: "error",
        scheduler_running: false,
        error: error.message,
      },
      500
    );
  }
}

import { Context } from "hono";
import type { Env, StatsResponse } from "../types";

export async function statsHandler(c: Context<{ Bindings: Env }>) {
  try {
    const env = c.env;

    // Get stats from KV
    const statsJson = await env.KV.get("stats.json");
    const stats = statsJson
      ? JSON.parse(statsJson)
      : {
          total_processed_batches: 0,
          total_processed_conversations: 0,
          total_callback_batches: 0,
        };

    const response: StatsResponse = {
      ...stats,
      last_check: new Date().toISOString(),
    };

    return c.json(response, 200);
  } catch (error: any) {
    return c.json({ error: error.message }, 500);
  }
}

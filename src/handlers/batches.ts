import { Context } from "hono";
import type { Env, Batch } from "../types";
import { processPipeline } from "../services/pipeline";

export async function batchesHandler(c: Context<{ Bindings: Env }>) {
  try {
    const env = c.env;

    // Get recent batch list from KV
    const batchList = await env.KV.get("batch_list.json");
    const batches: Batch[] = batchList ? JSON.parse(batchList) : [];

    // Return last 20 batches
    return c.json(
      {
        batches: batches.slice(0, 20),
        total: batches.length,
      },
      200
    );
  } catch (error: any) {
    return c.json({ error: error.message }, 500);
  }
}

export async function processHandler(c: Context<{ Bindings: Env }>) {
  try {
    const env = c.env;
    const batch_id = c.req.param("batch_id");

    if (!batch_id) {
      return c.json({ error: "batch_id required" }, 400);
    }

    // Process batch
    const result = await processPipeline(env, batch_id);

    return c.json(result, 200);
  } catch (error: any) {
    return c.json({ error: error.message }, 500);
  }
}

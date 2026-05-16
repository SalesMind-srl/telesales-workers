import { Context } from "hono";
import type { Env } from "../types";
import { processPipeline } from "../services/pipeline";
import { listCompletedBatches } from "../services/elevenlabs";

export async function cronHandler(
  c?: Context<{ Bindings: Env }> | { env: Env }
) {
  try {
    const env = (c as any)?.env || (c as any)?.bindings;

    // Log cron execution
    const cronTime = new Date().toISOString();
    console.log(`[CRON] Batch check started at ${cronTime}`);

    // Get list of completed batches from ElevenLabs
    const completedBatches = await listCompletedBatches(env, 50);
    console.log(
      `[CRON] Found ${completedBatches.length} completed batches from EL`
    );

    // Get processed batches from KV
    const processedJson = await env.KV.get("processed_batches.json");
    const processedIds: string[] = processedJson
      ? JSON.parse(processedJson)
      : [];

    // Filter new batches
    const newBatches = completedBatches.filter(
      (b: any) => !processedIds.includes(b.id)
    );
    console.log(`[CRON] ${newBatches.length} new batches to process`);

    // Process each new batch
    let successCount = 0;
    let errorCount = 0;

    for (const batch of newBatches) {
      try {
        await processPipeline(env, batch.id);
        successCount++;
        processedIds.push(batch.id);
      } catch (err) {
        console.error(`[CRON] Error processing batch ${batch.id}:`, err);
        errorCount++;
      }
    }

    // Update processed list in KV
    await env.KV.put("processed_batches.json", JSON.stringify(processedIds));

    // Update last check timestamp
    await env.KV.put("last_check_timestamp", cronTime);

    // Update stats
    const statsJson = await env.KV.get("stats.json");
    const stats = statsJson
      ? JSON.parse(statsJson)
      : {
          total_processed_batches: 0,
          total_processed_conversations: 0,
          total_callback_batches: 0,
        };

    stats.total_processed_batches += successCount;
    stats.last_check = cronTime;

    await env.KV.put("stats.json", JSON.stringify(stats));

    const result = {
      success: true,
      cronTime,
      newBatchesFound: newBatches.length,
      processed: successCount,
      errors: errorCount,
    };

    console.log(`[CRON] Completed: ${JSON.stringify(result)}`);
    return result;
  } catch (error: any) {
    console.error("[CRON] Fatal error:", error);
    return {
      success: false,
      error: error.message,
      cronTime: new Date().toISOString(),
    };
  }
}

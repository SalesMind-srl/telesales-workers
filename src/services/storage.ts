import type { Env, Batch } from "../types";

export async function saveBatchList(env: Env, batches: Batch[]): Promise<void> {
  await env.KV.put("batch_list.json", JSON.stringify(batches));
}

export async function getBatchList(env: Env): Promise<Batch[]> {
  const data = await env.KV.get("batch_list.json");
  return data ? JSON.parse(data) : [];
}

export async function addProcessedBatch(
  env: Env,
  batch_id: string
): Promise<void> {
  const processed = await env.KV.get("processed_batches.json");
  const ids: string[] = processed ? JSON.parse(processed) : [];

  if (!ids.includes(batch_id)) {
    ids.push(batch_id);
    await env.KV.put("processed_batches.json", JSON.stringify(ids));
  }
}

export async function isProcessed(
  env: Env,
  batch_id: string
): Promise<boolean> {
  const processed = await env.KV.get("processed_batches.json");
  const ids: string[] = processed ? JSON.parse(processed) : [];
  return ids.includes(batch_id);
}

export async function saveStats(
  env: Env,
  stats: Record<string, any>
): Promise<void> {
  await env.KV.put("stats.json", JSON.stringify(stats));
}

export async function getStats(env: Env): Promise<Record<string, any>> {
  const data = await env.KV.get("stats.json");
  return data
    ? JSON.parse(data)
    : {
        total_processed_batches: 0,
        total_processed_conversations: 0,
        total_callback_batches: 0,
      };
}

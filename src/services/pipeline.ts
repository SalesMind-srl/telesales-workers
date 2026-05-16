import type { Env, ProcessedResult } from "../types";
import {
  listCompletedBatches,
  extractConversationAnalysis,
} from "./elevenlabs";
import { appendResultToSheets } from "./sheets";

export async function processPipeline(
  env: Env,
  batch_id: string
): Promise<any> {
  try {
    console.log(`[PIPELINE] Processing batch ${batch_id}`);

    // Get batch from EL
    const batches = await listCompletedBatches(env, 100);
    const batch = batches.find((b: any) => b.id === batch_id);

    if (!batch) {
      throw new Error(`Batch ${batch_id} not found`);
    }

    const results: ProcessedResult[] = [];
    let errorCount = 0;

    // Process each conversation in batch
    const conversations = batch.conversations || [];
    console.log(`[PIPELINE] Processing ${conversations.length} conversations`);

    for (const conv of conversations) {
      try {
        // Extract analysis from EL
        const analysis = await extractConversationAnalysis(
          env,
          conv.conversation_id,
          conv.phone_number || "unknown"
        );

        const result: ProcessedResult = {
          batch_id,
          phone: analysis.phone,
          interest_level: analysis.interest_level,
          appointment_scheduled: analysis.appointment_scheduled,
          email: analysis.email,
          name: analysis.name,
          transcript_summary: analysis.transcript_summary,
          duration_secs: analysis.duration_secs,
          timestamp: new Date().toISOString(),
        };

        // Append to sheets
        const sheetId = await env.KV.get("GOOGLE_SHEETS_ID");
        if (sheetId) {
          await appendResultToSheets(env, sheetId.toString(), result);
        }

        results.push(result);
      } catch (err) {
        console.error(
          `[PIPELINE] Error processing conversation ${conv.conversation_id}:`,
          err
        );
        errorCount++;
      }
    }

    // Mark batch as processed
    const processedBatches = await env.KV.get("processed_batches.json");
    const processed: string[] = processedBatches
      ? JSON.parse(processedBatches)
      : [];

    if (!processed.includes(batch_id)) {
      processed.push(batch_id);
      await env.KV.put("processed_batches.json", JSON.stringify(processed));
    }

    console.log(
      `[PIPELINE] Batch ${batch_id} processed: ${results.length} results, ${errorCount} errors`
    );

    return {
      success: true,
      batch_id,
      processed: results.length,
      errors: errorCount,
      results,
    };
  } catch (error: any) {
    console.error(`[PIPELINE] Error processing batch:`, error);
    return {
      success: false,
      batch_id,
      error: error.message,
    };
  }
}

export async function processAllCompletedBatches(env: Env): Promise<any> {
  try {
    console.log("[PIPELINE] Scanning for completed batches...");

    // Get all batches from EL
    const allBatches = await listCompletedBatches(env, 100);

    // Get processed batches from KV
    const processedJson = await env.KV.get("processed_batches.json");
    const processedIds: string[] = processedJson
      ? JSON.parse(processedJson)
      : [];

    // Filter new completed batches
    const newBatches = allBatches.filter(
      (b: any) => b.status === "completed" && !processedIds.includes(b.id)
    );

    console.log(
      `[PIPELINE] Found ${newBatches.length} new batches to process`
    );

    let totalProcessed = 0;
    let totalErrors = 0;

    // Process each batch
    for (const batch of newBatches) {
      const result = await processPipeline(env, batch.id);
      if (result.success) {
        totalProcessed += result.processed;
      } else {
        totalErrors += 1;
      }
    }

    return {
      success: true,
      newBatchesProcessed: newBatches.length,
      totalConversationsProcessed: totalProcessed,
      totalErrors,
    };
  } catch (error: any) {
    console.error("[PIPELINE] Error processing batches:", error);
    return {
      success: false,
      error: error.message,
    };
  }
}

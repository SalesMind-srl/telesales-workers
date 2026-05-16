import type { Env, ProcessedResult } from "../types";

// Note: For now, this is a stub. You'll need to configure Google Sheets API credentials
// and add proper authentication using google-auth-library

export async function appendResultToSheets(
  env: Env,
  sheetId: string,
  result: ProcessedResult
): Promise<boolean> {
  try {
    // TODO: Implement Google Sheets API append
    // For MVP, we can log to KV instead and batch sync later

    // Store result in KV for batch processing
    const resultsKey = `sheet_results_${new Date().toISOString().split("T")[0]}`;
    const existingResults = await env.KV.get(resultsKey);
    const results: ProcessedResult[] = existingResults
      ? JSON.parse(existingResults)
      : [];

    results.push(result);
    await env.KV.put(resultsKey, JSON.stringify(results));

    console.log(
      `[SHEETS] Queued result for ${result.phone} (${result.interest_level})`
    );
    return true;
  } catch (error: any) {
    console.error("Error appending to Sheets:", error);
    return false;
  }
}

export async function appendBatchResultsToSheets(
  env: Env,
  sheetId: string,
  results: ProcessedResult[]
): Promise<number> {
  let successCount = 0;

  for (const result of results) {
    const success = await appendResultToSheets(env, sheetId, result);
    if (success) successCount++;
  }

  return successCount;
}

export async function getProcessedResultsFromQueue(
  env: Env,
  date?: string
): Promise<ProcessedResult[]> {
  try {
    const resultsKey = `sheet_results_${date || new Date().toISOString().split("T")[0]}`;
    const resultsJson = await env.KV.get(resultsKey);
    return resultsJson ? JSON.parse(resultsJson) : [];
  } catch (error: any) {
    console.error("Error retrieving queued results:", error);
    return [];
  }
}

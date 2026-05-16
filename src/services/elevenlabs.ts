import type { Env, ConversationAnalysis } from "../types";

const EL_BASE_URL = "https://api.elevenlabs.io";

export async function listCompletedBatches(env: Env, limit: number = 50) {
  try {
    const response = await fetch(
      `${EL_BASE_URL}/v1/convai/batch-calling/workspace?limit=${limit}`,
      {
        method: "GET",
        headers: {
          "xi-api-key": env.ELEVENLABS_API_KEY,
        },
      }
    );

    if (!response.ok) {
      throw new Error(`EL API error: ${response.status}`);
    }

    const data = await response.json();
    return data.batch_call_requests || [];
  } catch (error: any) {
    console.error("Error listing batches from EL:", error);
    throw error;
  }
}

export async function getConversation(
  env: Env,
  conversation_id: string
): Promise<any> {
  try {
    const response = await fetch(
      `${EL_BASE_URL}/v1/convai/conversations/${conversation_id}`,
      {
        method: "GET",
        headers: {
          "xi-api-key": env.ELEVENLABS_API_KEY,
        },
      }
    );

    if (!response.ok) {
      throw new Error(`EL API error: ${response.status}`);
    }

    return await response.json();
  } catch (error: any) {
    console.error(`Error fetching conversation ${conversation_id}:`, error);
    throw error;
  }
}

export async function getTranscript(
  env: Env,
  conversation_id: string
): Promise<string> {
  try {
    const response = await fetch(
      `${EL_BASE_URL}/v1/convai/conversations/${conversation_id}/transcript`,
      {
        method: "GET",
        headers: {
          "xi-api-key": env.ELEVENLABS_API_KEY,
        },
      }
    );

    if (!response.ok) {
      throw new Error(`EL API error: ${response.status}`);
    }

    const data = await response.json();
    return data.transcript || "";
  } catch (error: any) {
    console.error(`Error fetching transcript for ${conversation_id}:`, error);
    return "";
  }
}

export async function extractConversationAnalysis(
  env: Env,
  conversation_id: string,
  phone: string
): Promise<ConversationAnalysis> {
  try {
    const conv = await getConversation(env, conversation_id);

    const analysis: ConversationAnalysis = {
      phone,
      interest_level:
        conv.analysis?.data_collection_results?.interest_level?.value ||
        "none",
      appointment_scheduled:
        conv.analysis?.evaluation_criteria_results?.appointment_scheduled
          ?.result === "success",
      appointment_date_time:
        conv.analysis?.evaluation_criteria_results?.appointment_date_time
          ?.value,
      email:
        conv.analysis?.data_collection_results?.email?.value ||
        conv.analysis?.data_collection_results?.contact_person_email?.value,
      name:
        conv.analysis?.data_collection_results?.name?.value ||
        conv.analysis?.data_collection_results?.contact_person_name?.value,
      transcript_summary:
        conv.analysis?.transcript_summary ||
        (await getTranscript(env, conversation_id)),
      duration_secs: conv.metadata?.call_duration_secs || 0,
    };

    return analysis;
  } catch (error: any) {
    console.error(`Error extracting analysis for ${conversation_id}:`, error);
    return {
      phone,
      interest_level: "none",
      appointment_scheduled: false,
      duration_secs: 0,
    };
  }
}

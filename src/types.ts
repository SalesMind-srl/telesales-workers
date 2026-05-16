import type { KVNamespace } from "@cloudflare/workers-types";

export interface Env {
  KV: KVNamespace;
  ELEVENLABS_API_KEY: string;
  ANTHROPIC_API_KEY: string;
  GOOGLE_SHEETS_API_KEY: string;
  CHECK_INTERVAL_MINUTES: string;
  MONITORED_AGENT_IDS: string;
}

export interface Batch {
  id: string;
  name: string;
  status: "pending" | "processing" | "completed" | "failed";
  agent_id: string;
  phone_number_id: string;
  recipients_count: number;
  created_at: string;
  completed_at?: string;
}

export interface ConversationAnalysis {
  interest_level: "high" | "medium" | "low" | "none";
  appointment_scheduled: boolean;
  appointment_date_time?: string;
  email?: string;
  name?: string;
  phone: string;
  transcript_summary?: string;
  duration_secs: number;
}

export interface ProcessedResult {
  batch_id: string;
  phone: string;
  interest_level: string;
  appointment_scheduled: boolean;
  email?: string;
  name?: string;
  transcript_summary?: string;
  duration_secs: number;
  timestamp: string;
}

export interface HealthStatus {
  status: "ok" | "error";
  scheduler_running: boolean;
  last_check?: string;
  next_check?: string;
  error?: string;
}

export interface StatsResponse {
  total_processed_batches: number;
  total_processed_conversations: number;
  total_callback_batches: number;
  last_check: string;
}

export type Department = "software" | "ai" | "unknown" | "other";
export type CurriculumYear = "2023" | "2024" | "2025" | "unknown";

export interface Profile {
  id: string;
  exists: boolean;
  department: Department;
  grade: number;
  curriculum_year: CurriculumYear;
}

export interface MissingProfile {
  exists: false;
}

export interface Memory {
  id: string;
  category: string;
  key: string;
  value_json: Record<string, unknown>;
  natural_text: string;
  confidence: number;
  sensitivity: "low" | "medium" | "high";
  status: "candidate" | "active" | "archived" | "rejected";
  embedding_status: "pending" | "ready" | "failed";
}

export interface MemoryEvent {
  id: string;
  memory_id: string | null;
  event_type: string;
  reason: string | null;
  snapshot: Record<string, unknown>;
}

export interface ChatAction {
  type: string;
  label: string;
  payload: Record<string, unknown>;
}

export interface ChatEvidence {
  personalization: string[];
  internal_sources: Array<Record<string, unknown>>;
  web_sources: Array<Record<string, unknown>>;
  notes: string[];
}

export interface ChoiceOption {
  id: string;
  label: string;
  message: string;
}

export interface ChatResponse {
  session_id: string | null;
  answer: string;
  intent: string;
  actions: ChatAction[];
  evidence: ChatEvidence;
  choices: ChoiceOption[];
  memory_updates: Memory[];
  needs_verification: string[];
}

export interface ChatSessionSummary {
  id: string;
  title: string | null;
  intent: string | null;
}

export interface ChatMessageRecord {
  id: string;
  session_id: string;
  role: "user" | "assistant" | "system";
  content: string;
  evidence: Record<string, unknown>;
  memory_updates: Array<Record<string, unknown>>;
}

export interface Assignment {
  id: string;
  title: string;
  course: string | null;
  due_at: string;
  memo: string | null;
  status: "todo" | "done";
  calendar_event_id: string | null;
  calendar_synced_at: string | null;
  d_day: number;
  d_day_label: string;
}

export interface AssignmentPreview {
  title: string;
  course: string | null;
  due_at: string;
  memo: string | null;
  d_day: number;
  d_day_label: string;
  confidence: number;
  missing_fields: string[];
  parser: "python_rules" | "gemini";
}

export interface CalendarExportResponse {
  assignment_id: string;
  calendar_event_id: string;
  calendar_synced_at: string;
  already_exported: boolean;
  google_event: Record<string, unknown>;
}

export interface GoogleCalendarStatus {
  configured: boolean;
  connected: boolean;
  scope: string;
}

export interface GoogleCalendarConnectResponse {
  configured: boolean;
  authorization_url: string | null;
  scope: string;
  reason: string | null;
}

export interface RuntimeComponentStatus {
  configured: boolean;
  ready: boolean;
  missing_env: string[];
  missing_schema: string[];
  next_actions: string[];
  blocker: string | null;
}

export interface RuntimeStatus {
  mode: "live";
  supabase_backend: RuntimeComponentStatus;
  supabase_schema: RuntimeComponentStatus;
  gemini: RuntimeComponentStatus;
  google_calendar: RuntimeComponentStatus;
}

export interface RecommendationItem {
  id: string;
  title: string;
  score: number;
  reasons: string[];
  next_steps: string[];
}

export interface RecommendationEvidence {
  internal_sources: Array<Record<string, unknown>>;
}

export interface TrackRecommendResponse {
  primary_recommendation: RecommendationItem;
  recommendations: RecommendationItem[];
  recommended_actions: string[];
  evidence: RecommendationEvidence;
}

export interface ActivityRecommendResponse {
  activity_style: string;
  recommendations: RecommendationItem[];
  recommended_actions: string[];
  evidence: RecommendationEvidence;
}

export interface LLMUsageLog {
  id: string;
  user_id: string;
  feature: string;
  input_text: string;
  output_text: string | null;
  model: string | null;
  purpose: string;
  metadata: Record<string, unknown>;
  created_at: string;
}

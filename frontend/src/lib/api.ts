import type {
  Assignment,
  AssignmentPreview,
  ActivityRecommendResponse,
  CalendarExportResponse,
  ChatMessageRecord,
  ChatResponse,
  ChatSessionSummary,
  CurriculumYear,
  Department,
  GoogleCalendarConnectResponse,
  GoogleCalendarStatus,
  LLMUsageLog,
  Memory,
  MissingProfile,
  Profile,
  TrackRecommendResponse,
} from "../types/api";
import { getSupabaseAccessToken } from "./supabase";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

interface ProfileInput {
  department: Department;
  grade: number;
  curriculum_year: CurriculumYear;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const accessToken = await getSupabaseAccessToken();
  if (!accessToken) {
    throw new Error("Supabase 로그인 세션이 필요합니다.");
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${accessToken}`,
      ...init?.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`API 요청 실패: ${response.status}`);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export function getProfile(): Promise<Profile | MissingProfile> {
  return request<Profile | MissingProfile>("/api/profile");
}

export function upsertProfile(input: ProfileInput): Promise<Profile> {
  return request<Profile>("/api/profile", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export async function getMemories(): Promise<Memory[]> {
  const data = await request<{ memories: Memory[] }>("/api/memories");
  return data.memories;
}

export function updateMemory(memoryId: string, input: Partial<Pick<Memory, "natural_text" | "value_json">>): Promise<Memory> {
  return request<Memory>(`/api/memories/${memoryId}`, {
    method: "PATCH",
    body: JSON.stringify(input),
  });
}

export function deleteMemory(memoryId: string): Promise<Memory> {
  return request<Memory>(`/api/memories/${memoryId}`, {
    method: "DELETE",
  });
}

export async function getChatSessions(): Promise<ChatSessionSummary[]> {
  const data = await request<{ sessions: ChatSessionSummary[] }>("/api/chat/sessions");
  return data.sessions;
}

export async function getChatMessages(sessionId: string): Promise<ChatMessageRecord[]> {
  const data = await request<{ messages: ChatMessageRecord[] }>(
    `/api/chat/sessions/${sessionId}/messages`,
  );
  return data.messages;
}

export function sendChatMessage(message: string, sessionId?: string | null): Promise<ChatResponse> {
  return request<ChatResponse>("/api/chat", {
    method: "POST",
    body: JSON.stringify({ message, session_id: sessionId ?? null }),
  });
}

export function previewAssignment(text: string): Promise<AssignmentPreview> {
  return request<AssignmentPreview>("/api/assignments/preview", {
    method: "POST",
    body: JSON.stringify({ text }),
  });
}

export function createAssignment(input: {
  title: string;
  due_at: string;
  course?: string | null;
  memo?: string | null;
}): Promise<Assignment> {
  return request<Assignment>("/api/assignments", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export async function getAssignments(): Promise<Assignment[]> {
  const data = await request<{ assignments: Assignment[] }>("/api/assignments");
  return data.assignments;
}

export function updateAssignment(
  assignmentId: string,
  input: Partial<Pick<Assignment, "status">>,
): Promise<Assignment> {
  return request<Assignment>(`/api/assignments/${assignmentId}`, {
    method: "PATCH",
    body: JSON.stringify(input),
  });
}

export async function deleteAssignment(assignmentId: string): Promise<void> {
  await request<void>(`/api/assignments/${assignmentId}`, {
    method: "DELETE",
  });
}

export function exportAssignmentToCalendar(assignmentId: string): Promise<CalendarExportResponse> {
  return request<CalendarExportResponse>(`/api/assignments/${assignmentId}/export-calendar`, {
    method: "POST",
  });
}

export function getGoogleCalendarStatus(): Promise<GoogleCalendarStatus> {
  return request<GoogleCalendarStatus>("/api/integrations/google-calendar/status");
}

export function getGoogleCalendarConnectUrl(): Promise<GoogleCalendarConnectResponse> {
  return request<GoogleCalendarConnectResponse>("/api/integrations/google-calendar/connect");
}

export function recommendTrack(input: {
  grade: number;
  interests: string[];
  goal: string;
  coding_level: "beginner" | "intermediate" | "advanced";
  preference: "lecture" | "project" | "study" | "unknown";
}): Promise<TrackRecommendResponse> {
  return request<TrackRecommendResponse>("/api/recommend/track", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function recommendActivity(input: {
  interests: string[];
  activity_style: "solo" | "team" | "mixed" | "unknown";
  weekly_hours: number;
}): Promise<ActivityRecommendResponse> {
  return request<ActivityRecommendResponse>("/api/recommend/activity", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export async function getLLMUsageLogs(): Promise<LLMUsageLog[]> {
  const data = await request<{ logs: LLMUsageLog[] }>("/api/llm-logs");
  return data.logs;
}

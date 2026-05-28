import type {
  Assignment,
  AssignmentPreview,
  ActivityRecommendResponse,
  CalendarExportResponse,
  ChatAttachmentInput,
  ChatMessageRecord,
  ChatMode,
  ChatModelTier,
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
  RuntimeStatus,
  TrackRecommendResponse,
} from "../types/api";
import { getSupabaseAccessToken } from "./supabase";

const API_BASE_URL = normalizeApiBaseUrl(import.meta.env.VITE_API_BASE_URL || "");
const API_BASE_URLS = buildApiBaseUrls(API_BASE_URL);

function normalizeApiBaseUrl(url: string): string {
  return url.trim().replace(/\/+$/, "");
}

function buildApiBaseUrls(configuredBaseUrl: string): string[] {
  const urls = [configuredBaseUrl];
  if (import.meta.env.DEV) {
    urls.push("", "http://127.0.0.1:8000", "http://localhost:8000");
  }
  return [...new Set(urls.map(normalizeApiBaseUrl))];
}

function apiUrl(baseUrl: string, path: string): string {
  return `${baseUrl}${path}`;
}

async function fetchApi(path: string, init?: RequestInit): Promise<Response> {
  for (let attempt = 0; attempt < API_BASE_URLS.length; attempt += 1) {
    try {
      return await fetch(apiUrl(API_BASE_URLS[attempt], path), init);
    } catch (error) {
      if (isAbortError(error, init?.signal)) {
        throw error;
      }
      if (attempt === API_BASE_URLS.length - 1) {
        throw buildApiConnectionError();
      }
    }
  }
  throw buildApiConnectionError();
}

function isAbortError(error: unknown, signal?: AbortSignal | null): boolean {
  return Boolean(
    signal?.aborted || (error instanceof DOMException && error.name === "AbortError"),
  );
}

function buildApiConnectionError(): Error {
  if (import.meta.env.DEV) {
    return new Error("백엔드 API에 연결할 수 없습니다. 8000 포트 서버를 확인해 주세요.");
  }
  return new Error("서버에 연결할 수 없습니다. 잠시 후 다시 시도해 주세요.");
}

interface ProfileInput {
  department: Department;
  grade: number;
  curriculum_year: CurriculumYear;
}

export class ApiError extends Error {
  status: number;
  code: string | null;

  constructor(message: string, options: { status: number; code?: string | null }) {
    super(message);
    this.name = "ApiError";
    this.status = options.status;
    this.code = options.code ?? null;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const accessToken = await getSupabaseAccessToken();
  if (!accessToken) {
    throw new Error("로그인이 필요합니다.");
  }

  const response = await fetchApi(path, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${accessToken}`,
      ...init?.headers,
    },
  });

  if (!response.ok) {
    throw await buildApiError(response);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

async function publicRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetchApi(path, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });

  if (!response.ok) {
    throw await buildApiError(response);
  }

  return response.json() as Promise<T>;
}

async function buildApiError(response: Response): Promise<ApiError> {
  const fallback = `요청 실패: ${response.status}`;
  try {
    const payload = await response.json();
    const detail = typeof payload.detail === "string" ? payload.detail : fallback;
    const code = typeof payload.code === "string" ? payload.code : null;
    return new ApiError(detail, { status: response.status, code });
  } catch {
    return new ApiError(fallback, { status: response.status });
  }
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

export function createMemory(input: {
  natural_text: string;
  category: string;
  key: string;
  value_json: Record<string, unknown>;
}): Promise<Memory> {
  return request<Memory>("/api/memories", {
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

export function deleteChatSession(sessionId: string): Promise<void> {
  return request<void>(`/api/chat/sessions/${sessionId}`, {
    method: "DELETE",
  });
}

export function sendChatMessage(
  message: string,
  sessionId?: string | null,
  options?: {
    mode?: ChatMode;
    modelTier?: ChatModelTier;
    attachments?: ChatAttachmentInput[];
  },
): Promise<ChatResponse> {
  return request<ChatResponse>("/api/chat", {
    method: "POST",
    body: JSON.stringify({
      message,
      session_id: sessionId ?? null,
      mode: options?.mode ?? "auto",
      model_tier: options?.modelTier ?? "balanced",
      attachments: options?.attachments ?? [],
    }),
  });
}

export async function streamChatMessage(
  message: string,
  sessionId: string | null | undefined,
  options: {
    mode?: ChatMode;
    modelTier?: ChatModelTier;
    attachments?: ChatAttachmentInput[];
    signal?: AbortSignal;
  },
  handlers: {
    onSession?: (sessionId: string | null) => void;
    onText?: (delta: string) => void;
    onDone?: (response: ChatResponse) => void;
    onStatus?: (message: string) => void;
  },
): Promise<ChatResponse> {
  const accessToken = await getSupabaseAccessToken();
  if (!accessToken) {
    throw new Error("로그인이 필요합니다.");
  }

  const response = await fetchApi("/api/chat/stream", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "text/event-stream",
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify({
      message,
      session_id: sessionId ?? null,
      mode: options.mode ?? "auto",
      model_tier: options.modelTier ?? "balanced",
      attachments: options.attachments ?? [],
    }),
    signal: options.signal,
  });

  if (!response.ok) {
    throw await buildApiError(response);
  }
  if (!response.body) {
    throw new Error("스트리밍 응답을 열 수 없습니다.");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let finalResponse: ChatResponse | null = null;

  while (true) {
    const { value, done } = await reader.read();
    if (done) {
      break;
    }
    buffer += decoder.decode(value, { stream: true });
    const frames = buffer.split(/\r?\n\r?\n/);
    buffer = frames.pop() ?? "";
    for (const frame of frames) {
      const parsed = parseSseFrame(frame);
      if (!parsed) {
        continue;
      }
      if (parsed.event === "status") {
        handlers.onStatus?.(String(parsed.data.message ?? ""));
      } else if (parsed.event === "session") {
        handlers.onSession?.(typeof parsed.data.session_id === "string" ? parsed.data.session_id : null);
      } else if (parsed.event === "text") {
        handlers.onText?.(String(parsed.data.delta ?? ""));
      } else if (parsed.event === "done") {
        finalResponse = parsed.data as unknown as ChatResponse;
        handlers.onDone?.(finalResponse);
      } else if (parsed.event === "error") {
        throw new Error(String(parsed.data.message ?? "채팅 스트리밍에 실패했습니다."));
      }
    }
  }
  const trailingFrame = buffer.trim();
  if (trailingFrame) {
    const parsed = parseSseFrame(trailingFrame);
    if (parsed?.event === "done") {
      finalResponse = parsed.data as unknown as ChatResponse;
      handlers.onDone?.(finalResponse);
    } else if (parsed?.event === "error") {
      throw new Error(String(parsed.data.message ?? "채팅 스트리밍에 실패했습니다."));
    }
  }

  if (!finalResponse) {
    throw new Error("채팅 응답이 완료되지 않았습니다.");
  }
  return finalResponse;
}

function parseSseFrame(frame: string): { event: string; data: Record<string, unknown> } | null {
  let event = "message";
  const dataLines: string[] = [];
  for (const line of frame.split(/\r?\n/)) {
    if (line.startsWith("event:")) {
      event = line.slice("event:".length).trim();
    }
    if (line.startsWith("data:")) {
      dataLines.push(line.slice("data:".length).trimStart());
    }
  }
  if (!dataLines.length) {
    return null;
  }
  return { event, data: JSON.parse(dataLines.join("\n")) as Record<string, unknown> };
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

export function getRuntimeStatus(): Promise<RuntimeStatus> {
  return request<RuntimeStatus>("/api/runtime/status");
}

export function getPublicRuntimeStatus(): Promise<RuntimeStatus> {
  return publicRequest<RuntimeStatus>("/api/runtime/public-status");
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

import {
  ChevronDown,
  ChevronRight,
  CheckCircle2,
  Lightbulb,
  LogIn,
  LogOut,
  Paperclip,
  Send,
  SlidersHorizontal,
  Square,
  X,
} from "lucide-react";
import { cjk } from "@streamdown/cjk";
import { FormEvent, type ReactNode, useEffect, useMemo, useRef, useState } from "react";
import { Streamdown } from "streamdown";
import { Toaster, toast } from "sonner";

import { Sidebar, MobileDrawer } from "./components/navigation";
import { TopBar } from "./components/TopBar";
import {
  ApiError,
  createMemory,
  deleteChatSession,
  getChatMessages,
  getChatSessions,
  createAssignment,
  deleteAssignment,
  getAssignments,
  getMemories,
  getLLMUsageLogs,
  getProfile,
  previewAssignment,
  recommendActivity,
  recommendTrack,
  streamChatMessage,
  updateAssignment,
  upsertProfile,
} from "./lib/api";
import {
  getAuthSession,
  getSupabaseClient,
  signInWithEmailPassword,
  signOutSupabase,
  signUpWithEmailPassword,
  type AuthSessionSummary,
} from "./lib/supabase";
import {
  buildRecommendationInputContext,
  recommendationContextToDraft,
  recommendationDraftToContext,
} from "./lib/navigator";
import type {
  Assignment,
  ActivityRecommendResponse,
  AssignmentPreview,
  ChatResponse,
  ChatAttachmentInput,
  ChatMode,
  ChatModelTier,
  ChatMessageRecord,
  ChatSessionSummary,
  LLMUsageLog,
  Memory,
  MissingProfile,
  Profile,
  Department,
  CurriculumYear,
  TrackRecommendResponse,
} from "./types/api";
import type {
  ChatMessage,
  RecommendationInputContext,
  RecommendationInputDraft,
  WorkspacePage,
} from "./types/navigator";

function getErrorMessage(error: unknown, fallback: string): string {
  if (error instanceof ApiError && error.code === "supabase_schema_missing") {
    return "서비스 저장소를 준비하는 중입니다. 잠시 후 다시 시도해 주세요.";
  }
  return error instanceof Error ? error.message : fallback;
}

function getAuthErrorMessage(error: unknown): string {
  const rawMessage = error instanceof Error ? error.message : "";
  const normalized = rawMessage.toLowerCase();
  if (normalized.includes("anonymous sign-ins")) {
    return "이메일과 비밀번호를 입력해 주세요.";
  }
  if (normalized.includes("invalid login credentials")) {
    return "이메일 또는 비밀번호가 맞지 않습니다.";
  }
  if (normalized.includes("email not confirmed")) {
    return "이메일 확인 후 다시 로그인해 주세요.";
  }
  if (normalized.includes("password should be at least")) {
    return "비밀번호는 6자 이상으로 입력해 주세요.";
  }
  if (normalized.includes("unable to validate email") || normalized.includes("invalid email")) {
    return "이메일 형식을 확인해 주세요.";
  }
  return rawMessage || "인증 요청에 실패했습니다.";
}

async function readAttachmentText(file: File): Promise<string | null> {
  const textLike =
    file.type.startsWith("text/") ||
    [
      ".md",
      ".csv",
      ".json",
      ".py",
      ".ts",
      ".tsx",
      ".js",
      ".jsx",
      ".html",
      ".css",
    ].some((extension) => file.name.toLowerCase().endsWith(extension));
  if (!textLike || file.size > 500_000) {
    return null;
  }
  const text = await file.text();
  return text.slice(0, 12_000);
}

const ACTIVE_CHAT_SESSION_KEY = "kmu:active_chat_session";
const CHAT_RESPONSE_METADATA_KEY = "__response";

function buildStoredChatResponse(record: ChatMessageRecord): ChatResponse | undefined {
  if (record.role !== "assistant") {
    return undefined;
  }

  const evidence = record.evidence ?? {};
  const metadata = isRecord(evidence[CHAT_RESPONSE_METADATA_KEY])
    ? evidence[CHAT_RESPONSE_METADATA_KEY]
    : {};
  const cleanEvidence = {
    personalization: arrayOfStrings(evidence.personalization),
    internal_sources: arrayOfRecords(evidence.internal_sources),
    web_sources: arrayOfRecords(evidence.web_sources),
    notes: arrayOfStrings(evidence.notes),
  };

  return {
    session_id: record.session_id,
    answer: record.content,
    intent: typeof metadata.intent === "string" ? metadata.intent : "general",
    model: typeof metadata.model === "string" ? metadata.model : null,
    actions: arrayOfRecords(metadata.actions).map((action) => ({
      type: typeof action.type === "string" ? action.type : "unknown",
      label: typeof action.label === "string" ? action.label : "작업",
      payload: isRecord(action.payload) ? action.payload : {},
    })),
    evidence: cleanEvidence,
    choices: arrayOfRecords(metadata.choices).map((choice, index) => ({
      id: typeof choice.id === "string" ? choice.id : `stored-choice-${index}`,
      label: typeof choice.label === "string" ? choice.label : "이어서 질문하기",
      message: typeof choice.message === "string" ? choice.message : "",
    })).filter((choice) => choice.message),
    memory_updates: record.memory_updates as unknown as Memory[],
    needs_verification: arrayOfStrings(metadata.needs_verification),
  };
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

function arrayOfRecords(value: unknown): Array<Record<string, unknown>> {
  return Array.isArray(value) ? value.filter(isRecord) : [];
}

function arrayOfStrings(value: unknown): string[] {
  return Array.isArray(value) ? value.filter((item): item is string => typeof item === "string") : [];
}

interface ProfileInput {
  department: Department;
  grade: number;
  curriculum_year: CurriculumYear;
  interests_text: string;
  goal: string;
  coding_level: RecommendationInputContext["codingLevel"];
  preference: RecommendationInputContext["preference"];
  activity_style: RecommendationInputContext["activityStyle"];
  weekly_hours: number;
}

interface ComposerAttachment extends ChatAttachmentInput {
  id: string;
}

export default function App() {
  const [activePage, setActivePage] = useState<WorkspacePage>("chat");
  const [profile, setProfile] = useState<Profile | MissingProfile | null>(null);
  const [memories, setMemories] = useState<Memory[]>([]);
  const [chatSessions, setChatSessions] = useState<ChatSessionSummary[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [draft, setDraft] = useState("");
  const [chatMode, setChatMode] = useState<ChatMode>("auto");
  const [chatModelTier, setChatModelTier] = useState<ChatModelTier>("balanced");
  const [composerAttachments, setComposerAttachments] = useState<ComposerAttachment[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthChecked, setIsAuthChecked] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [authSession, setAuthSession] = useState<AuthSessionSummary | null>(null);
  const [authEmail, setAuthEmail] = useState("");
  const [authPassword, setAuthPassword] = useState("");
  const [authStatus, setAuthStatus] = useState<string | null>(null);
  const [authMode, setAuthMode] = useState<"signin" | "signup">("signin");
  const [isAuthBusy, setIsAuthBusy] = useState(false);
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [assignmentDraft, setAssignmentDraft] = useState("자료구조 과제 다음주 금요일까지");
  const [assignmentPreview, setAssignmentPreview] = useState<AssignmentPreview | null>(null);
  const [llmUsageLogs, setLlmUsageLogs] = useState<LLMUsageLog[]>([]);
  const [trackResult, setTrackResult] = useState<TrackRecommendResponse | null>(null);
  const [activityResult, setActivityResult] = useState<ActivityRecommendResponse | null>(null);
  const [isMobileNavOpen, setIsMobileNavOpen] = useState(false);
  const [isMobileContextOpen, setIsMobileContextOpen] = useState(false);
  const [isRecommendationEdited, setIsRecommendationEdited] = useState(false);
  const [onboardingDraft, setOnboardingDraft] = useState<ProfileInput>({
    department: "software",
    grade: 1,
    curriculum_year: "2025",
    interests_text: "AI, 백엔드",
    goal: "AI 서비스 개발",
    coding_level: "beginner",
    preference: "project",
    activity_style: "team",
    weekly_hours: 4,
  });
  const activeChatAbortRef = useRef<AbortController | null>(null);

  const latestAssistantResponse = [...messages]
    .reverse()
    .find((message) => message.role === "assistant" && message.response)?.response;
  const automaticRecommendationInput = useMemo(
    () => buildRecommendationInputContext(memories),
    [memories],
  );
  const [recommendationDraft, setRecommendationDraft] = useState<RecommendationInputDraft>(() =>
    recommendationContextToDraft(automaticRecommendationInput),
  );
  const recommendationInput = useMemo(
    () =>
      recommendationDraftToContext(
        recommendationDraft,
        isRecommendationEdited
          ? `${automaticRecommendationInput.sourceLabel} + 직접 입력`
          : automaticRecommendationInput.sourceLabel,
      ),
    [recommendationDraft, automaticRecommendationInput.sourceLabel, isRecommendationEdited],
  );

  useEffect(() => {
    if (!isRecommendationEdited) {
      setRecommendationDraft(recommendationContextToDraft(automaticRecommendationInput));
    }
  }, [automaticRecommendationInput, isRecommendationEdited]);

  async function loadChatSessionMessages(sessionId: string): Promise<ChatMessage[]> {
    const records = await getChatMessages(sessionId);
    return records
      .filter((record) => record.role !== "system")
      .map((record) => ({
        id: record.id,
        role: record.role === "assistant" ? "assistant" : "user",
        text: record.content,
        response: buildStoredChatResponse(record),
      }));
  }

  async function refresh() {
    setError(null);
    setIsLoading(true);
    try {
      const session = await getAuthSession();
      setAuthSession(session);
      if (!session) {
        setProfile(null);
        setMemories([]);
        setChatSessions([]);
        setAssignments([]);
        setLlmUsageLogs([]);
        return;
      }
      const [profileData, memoryData, sessionsData, llmLogData] = await Promise.all([
        getProfile(),
        getMemories(),
        getChatSessions(),
        getLLMUsageLogs(),
      ]);
      setProfile(profileData);
      setMemories(memoryData);
      setChatSessions(sessionsData);
      setLlmUsageLogs(llmLogData);
      const savedSessionId = window.localStorage.getItem(ACTIVE_CHAT_SESSION_KEY);
      const sessionToRestore =
        sessionsData.find((session) => session.id === savedSessionId)?.id ?? sessionsData[0]?.id;
      if (sessionToRestore && !activeSessionId && messages.length === 0) {
        setActiveSessionId(sessionToRestore);
        setMessages(await loadChatSessionMessages(sessionToRestore));
      }
      setAssignments(await getAssignments());
    } catch (apiError) {
      const message = getErrorMessage(apiError, "데이터를 불러오지 못했습니다.");
      setError(message);
      toast.error(message);
    } finally {
      setIsLoading(false);
    }
  }

  async function refreshAuthSession() {
    setAuthSession(await getAuthSession());
    setIsAuthChecked(true);
  }

  async function handleAuthSubmit(mode: "signin" | "signup") {
    setAuthStatus(null);
    setError(null);
    if (!authEmail.trim() || !authPassword.trim()) {
      setAuthStatus("이메일과 비밀번호를 입력해 주세요.");
      return;
    }
    setIsAuthBusy(true);
    try {
      if (mode === "signin") {
        await signInWithEmailPassword(authEmail, authPassword);
        setAuthStatus("로그인되었습니다.");
        toast.success("로그인되었습니다.");
      } else {
        await signUpWithEmailPassword(authEmail, authPassword);
        setAuthStatus("가입 요청이 완료되었습니다. 이메일 확인이 필요할 수 있습니다.");
        toast.success("가입 요청이 완료되었습니다.");
      }
      await refreshAuthSession();
      await refresh();
    } catch (authError) {
      const message = getAuthErrorMessage(authError);
      setAuthStatus(message);
      toast.error(message);
    } finally {
      setIsAuthBusy(false);
    }
  }

  async function handleSignOut() {
    setAuthStatus(null);
    setError(null);
    setIsAuthBusy(true);
    try {
      await signOutSupabase();
      setAuthSession(null);
      setProfile(null);
      setMemories([]);
      setChatSessions([]);
      setAssignments([]);
      setMessages([]);
      setActiveSessionId(null);
      window.localStorage.removeItem(ACTIVE_CHAT_SESSION_KEY);
      setAuthStatus("로그아웃되었습니다.");
      toast.success("로그아웃되었습니다.");
    } catch (authError) {
      const message = getErrorMessage(authError, "로그아웃에 실패했습니다.");
      setAuthStatus(message);
      toast.error(message);
    } finally {
      setIsAuthBusy(false);
    }
  }

  async function handlePreviewAssignment() {
    setError(null);
    try {
      setAssignmentPreview(await previewAssignment(assignmentDraft));
      toast.success("일정 미리보기를 만들었습니다.");
    } catch (apiError) {
      const message = getErrorMessage(apiError, "일정 미리보기에 실패했습니다.");
      setError(message);
      toast.error(message);
    }
  }

  async function handleSaveAssignment() {
    if (!assignmentPreview) {
      return;
    }
    setError(null);
    try {
      const saved = await createAssignment({
        title: assignmentPreview.title,
        due_at: assignmentPreview.due_at,
        course: assignmentPreview.course,
        memo: assignmentPreview.memo,
      });
      setAssignments((current) => [saved, ...current]);
      setAssignmentPreview(null);
      toast.success("일정을 저장했습니다.");
    } catch (apiError) {
      const message = getErrorMessage(apiError, "일정 저장에 실패했습니다.");
      setError(message);
      toast.error(message);
    }
  }

  async function handleCompleteAssignment(assignmentId: string) {
    setError(null);
    try {
      const updated = await updateAssignment(assignmentId, { status: "done" });
      setAssignments((current) => current.filter((assignment) => assignment.id !== updated.id));
      toast.success("일정을 완료 처리했습니다.");
    } catch (apiError) {
      const message = getErrorMessage(apiError, "일정 완료 처리에 실패했습니다.");
      setError(message);
      toast.error(message);
    }
  }

  async function handleDeleteAssignment(assignmentId: string) {
    setError(null);
    try {
      await deleteAssignment(assignmentId);
      setAssignments((current) => current.filter((assignment) => assignment.id !== assignmentId));
      toast.success("일정을 삭제했습니다.");
    } catch (apiError) {
      const message = getErrorMessage(apiError, "일정 삭제에 실패했습니다.");
      setError(message);
      toast.error(message);
    }
  }

  async function handleRecommend() {
    setError(null);
    try {
      const [track, activity] = await Promise.all([
        recommendTrack({
          grade: profile?.exists ? profile.grade : 1,
          interests: recommendationInput.trackInterests,
          goal: recommendationInput.goal,
          coding_level: recommendationInput.codingLevel,
          preference: recommendationInput.preference,
        }),
        recommendActivity({
          interests: recommendationInput.activityInterests,
          activity_style: recommendationInput.activityStyle,
          weekly_hours: recommendationInput.weeklyHours,
        }),
      ]);
      setTrackResult(track);
      setActivityResult(activity);
      toast.success("추천 결과를 갱신했습니다.");
    } catch (apiError) {
      const message = getErrorMessage(apiError, "추천 요청에 실패했습니다.");
      setError(message);
      toast.error(message);
    }
  }

  function updateRecommendationDraft(patch: Partial<RecommendationInputDraft>) {
    setIsRecommendationEdited(true);
    setRecommendationDraft((current) => ({ ...current, ...patch }));
  }

  function resetRecommendationDraft() {
    setIsRecommendationEdited(false);
    setRecommendationDraft(recommendationContextToDraft(automaticRecommendationInput));
  }

  async function handleComposerFiles(files: FileList | null) {
    if (!files?.length) {
      return;
    }
    const nextAttachments: ComposerAttachment[] = [];
    for (const file of Array.from(files).slice(0, 3 - composerAttachments.length)) {
      const textContent = await readAttachmentText(file);
      nextAttachments.push({
        id: `${file.name}-${file.size}-${file.lastModified}`,
        name: file.name,
        mime_type: file.type || "application/octet-stream",
        size: file.size,
        text_content: textContent,
      });
    }
    setComposerAttachments((current) => [...current, ...nextAttachments].slice(0, 3));
  }

  function removeComposerAttachment(attachmentId: string) {
    setComposerAttachments((current) =>
      current.filter((attachment) => attachment.id !== attachmentId),
    );
  }

  function stopChatResponse() {
    activeChatAbortRef.current?.abort();
  }

  async function saveOnboardingProfile() {
    setError(null);
    try {
      const savedProfile = await upsertProfile({
        department: onboardingDraft.department,
        grade: onboardingDraft.grade,
        curriculum_year: onboardingDraft.curriculum_year,
      });
      const interests = splitOnboardingTerms(onboardingDraft.interests_text);
      if (interests.length || onboardingDraft.goal.trim()) {
        await createMemory({
          natural_text: buildOnboardingMemoryText(onboardingDraft, interests),
          category: "onboarding",
          key: "learning_context",
          value_json: {
            interests,
            goal: onboardingDraft.goal.trim(),
            coding_level: onboardingDraft.coding_level,
            preference: onboardingDraft.preference,
            activity_style: onboardingDraft.activity_style,
            weekly_hours: onboardingDraft.weekly_hours,
          },
        });
      }
      setProfile(savedProfile);
      setDraft(buildFirstQuestion(onboardingDraft, interests));
      setRecommendationDraft(
        recommendationContextToDraft({
          trackInterests: interests.length ? interests : ["AI", "백엔드"],
          activityInterests: interests.length ? interests : ["개발"],
          goal: onboardingDraft.goal.trim() || "AI 서비스 개발",
          codingLevel: onboardingDraft.coding_level,
          preference: onboardingDraft.preference,
          activityStyle: onboardingDraft.activity_style,
          weeklyHours: onboardingDraft.weekly_hours,
          sourceLabel: "처음 설정한 정보",
        }),
      );
      setIsRecommendationEdited(false);
      setActivePage("chat");
      toast.success("기본 정보를 저장했습니다.");
      await refresh();
    } catch (apiError) {
      const message = getErrorMessage(apiError, "기본 정보 저장에 실패했습니다.");
      setError(message);
      toast.error(message);
    }
  }

  async function handleSend(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const message = draft.trim();
    if (!message || isSending) {
      return;
    }

    setError(null);
    setIsSending(true);
    setDraft("");
    const abortController = new AbortController();
    activeChatAbortRef.current = abortController;
    const attachmentsForRequest = composerAttachments.map(({ id: _id, ...attachment }) => attachment);
    setComposerAttachments([]);
    const now = Date.now();
    const assistantMessageId = `assistant-${now}`;
    let visibleText = "";
    setMessages((current) => [
      ...current,
      { id: `user-${now}`, role: "user", text: message },
      { id: assistantMessageId, role: "assistant", text: "", isPending: true },
    ]);

    try {
      const response = await streamChatMessage(
        message,
        activeSessionId,
        {
          mode: chatMode,
          modelTier: chatModelTier,
          attachments: attachmentsForRequest,
          signal: abortController.signal,
        },
        {
          onSession: (sessionId) => {
            setActiveSessionId(sessionId);
            if (sessionId) {
              window.localStorage.setItem(ACTIVE_CHAT_SESSION_KEY, sessionId);
            }
          },
          onStatus: () => {
            setMessages((current) =>
              current.map((item) =>
                item.id === assistantMessageId
                  ? { ...item, isPending: true }
                  : item,
              ),
            );
          },
          onText: (delta) => {
            visibleText += delta;
            setMessages((current) =>
              current.map((item) =>
                item.id === assistantMessageId
                  ? { ...item, isPending: false, text: visibleText }
                  : item,
              ),
            );
          },
          onDone: (doneResponse) => {
            setActiveSessionId(doneResponse.session_id);
            if (doneResponse.session_id) {
              window.localStorage.setItem(ACTIVE_CHAT_SESSION_KEY, doneResponse.session_id);
            }
            setMessages((current) =>
              current.map((item) =>
                item.id === assistantMessageId
                  ? {
                      ...item,
                      isPending: false,
                      text: doneResponse.answer,
                      response: doneResponse,
                    }
                  : item,
              ),
            );
          },
        },
      );
      if (response.session_id) {
        setActiveSessionId(response.session_id);
        window.localStorage.setItem(ACTIVE_CHAT_SESSION_KEY, response.session_id);
      }
      void refreshChatSessions();
      toast.success("AI 답변을 받았습니다.");
    } catch (apiError) {
      if (apiError instanceof DOMException && apiError.name === "AbortError") {
        setMessages((current) =>
          current.map((item) =>
            item.id === assistantMessageId
              ? {
                  ...item,
                  isPending: false,
                  text: visibleText || "답변 생성을 중지했습니다.",
                }
              : item,
          ),
        );
        toast.info("답변 생성을 중지했습니다.");
        return;
      }
      const message = getErrorMessage(apiError, "채팅 요청에 실패했습니다.");
      setMessages((current) => current.filter((item) => item.id !== assistantMessageId));
      setComposerAttachments((current) => [...attachmentsForRequest.map((attachment) => ({
        ...attachment,
        id: `${attachment.name}-${attachment.size}-${Date.now()}`,
      })), ...current].slice(0, 3));
      setError(message);
      toast.error(message);
    } finally {
      setIsSending(false);
      if (activeChatAbortRef.current === abortController) {
        activeChatAbortRef.current = null;
      }
    }
  }

  async function refreshChatSessions() {
    try {
      setChatSessions(await getChatSessions());
    } catch {
      // 채팅 목록 실패는 상담 흐름을 막지 않으므로 상단 error 대신 목록만 유지한다.
    }
  }

  async function openChatSession(sessionId: string) {
    setError(null);
    setActivePage("chat");
    setIsMobileNavOpen(false);
    setActiveSessionId(sessionId);
    window.localStorage.setItem(ACTIVE_CHAT_SESSION_KEY, sessionId);
    try {
      setMessages(await loadChatSessionMessages(sessionId));
    } catch (apiError) {
      const message = getErrorMessage(apiError, "채팅 기록을 불러오지 못했습니다.");
      setError(message);
      toast.error(message);
    }
  }

  async function handleDeleteChatSession(sessionId: string) {
    setError(null);
    try {
      await deleteChatSession(sessionId);
      setChatSessions((current) => current.filter((session) => session.id !== sessionId));
      if (activeSessionId === sessionId) {
        setActiveSessionId(null);
        setMessages([]);
        window.localStorage.removeItem(ACTIVE_CHAT_SESSION_KEY);
      }
      toast.success("상담 기록을 삭제했습니다.");
      void refreshChatSessions();
    } catch (apiError) {
      const message = getErrorMessage(apiError, "상담 기록 삭제에 실패했습니다.");
      setError(message);
      toast.error(message);
    }
  }

  function startNewChat() {
    setActivePage("chat");
    setIsMobileNavOpen(false);
    setActiveSessionId(null);
    window.localStorage.removeItem(ACTIVE_CHAT_SESSION_KEY);
    setMessages([]);
    setDraft("수강신청 전에 AI 트랙 기준으로 어떤 과목을 볼까?");
  }

  function handleSelectPage(page: WorkspacePage) {
    setActivePage(page);
    setIsMobileNavOpen(false);
  }

  useEffect(() => {
    void refreshAuthSession().then(() => void refresh());
    const supabase = getSupabaseClient();
    const subscription = supabase?.auth.onAuthStateChange((_event, session) => {
      setAuthSession(
        session
          ? {
              userId: session.user.id,
              email: session.user.email ?? null,
            }
          : null,
      );
      if (session) {
        void refresh();
      } else {
        setProfile(null);
        setMemories([]);
        setChatSessions([]);
        setAssignments([]);
        setMessages([]);
        setActiveSessionId(null);
        setLlmUsageLogs([]);
        window.localStorage.removeItem(ACTIVE_CHAT_SESSION_KEY);
        setIsLoading(false);
      }
    });
    return () => {
      subscription?.data.subscription.unsubscribe();
    };
  }, []);

  if (!isAuthChecked) {
    return (
      <FullPageShell>
        <div className="text-sm font-semibold text-[#716c63]">세션을 확인하는 중입니다.</div>
      </FullPageShell>
    );
  }

  if (!authSession) {
    return (
      <LoginPage
        authMode={authMode}
        authEmail={authEmail}
        authPassword={authPassword}
        authStatus={authStatus}
        isAuthBusy={isAuthBusy}
        setAuthMode={setAuthMode}
        clearAuthStatus={() => setAuthStatus(null)}
        setAuthEmail={setAuthEmail}
        setAuthPassword={setAuthPassword}
        onAuthSubmit={(mode) => void handleAuthSubmit(mode)}
      />
    );
  }

  if (!isLoading && profile && !profile.exists) {
    return (
      <OnboardingPage
        authSession={authSession}
        draft={onboardingDraft}
        setDraft={setOnboardingDraft}
        onSave={() => void saveOnboardingProfile()}
        onSignOut={() => void handleSignOut()}
      />
    );
  }

  return (
    <main className="h-screen overflow-hidden bg-[#faf8f3] text-[#191817]">
      <Toaster richColors position="top-right" />
      <div className="grid h-full grid-cols-1 lg:grid-cols-[272px_minmax(0,1fr)_336px]">
        <Sidebar
          activePage={activePage}
          activeSessionId={activeSessionId}
          sessions={chatSessions}
          setActivePage={handleSelectPage}
          onNewChat={startNewChat}
          onOpenSession={(sessionId) => void openChatSession(sessionId)}
          onDeleteSession={(sessionId) => void handleDeleteChatSession(sessionId)}
        />

        <section className="grid min-w-0 grid-rows-[64px_minmax(0,1fr)] bg-[#faf8f3]">
          <TopBar
            activePage={activePage}
            error={error}
            isLoading={isLoading}
            onOpenMobileContext={() => setIsMobileContextOpen(true)}
            onRefresh={() => void refresh()}
            onOpenMobileNav={() => setIsMobileNavOpen(true)}
          />

          {activePage === "chat" ? (
            profile === null && error ? (
              <InlineDataLoadError
                error={error}
                onRefresh={() => void refresh()}
                onSignOut={() => void handleSignOut()}
              />
            ) : (
              <ChatWorkspace
                draft={draft}
                mode={chatMode}
                modelTier={chatModelTier}
                attachments={composerAttachments}
                messages={messages}
                isBootstrapping={isLoading && messages.length === 0}
                isSending={isSending}
                setDraft={setDraft}
                setMode={setChatMode}
                setModelTier={setChatModelTier}
                onAttachFiles={(files) => void handleComposerFiles(files)}
                onRemoveAttachment={removeComposerAttachment}
                onSend={handleSend}
                onStop={stopChatResponse}
              />
            )
          ) : activePage === "schedule" ? (
            <SchedulePage
              assignments={assignments}
              draft={assignmentDraft}
              preview={assignmentPreview}
              setDraft={setAssignmentDraft}
              onPreview={() => void handlePreviewAssignment()}
              onSave={() => void handleSaveAssignment()}
              onComplete={(assignmentId) => void handleCompleteAssignment(assignmentId)}
              onDelete={(assignmentId) => void handleDeleteAssignment(assignmentId)}
            />
          ) : activePage === "logs" ? (
            <LogsPage logs={llmUsageLogs} />
          ) : activePage === "career" ? (
            <RecommendationPage
              trackResult={trackResult}
              activityResult={activityResult}
              inputContext={recommendationInput}
              inputDraft={recommendationDraft}
              isEdited={isRecommendationEdited}
              onRecommend={() => void handleRecommend()}
              onResetInput={resetRecommendationDraft}
              onUpdateInput={updateRecommendationDraft}
            />
          ) : activePage === "settings" ? (
            <SettingsPage
              authEmail={authEmail}
              authPassword={authPassword}
              authSession={authSession}
              authStatus={authStatus}
              isAuthBusy={isAuthBusy}
              setAuthEmail={setAuthEmail}
              setAuthPassword={setAuthPassword}
              onAuthSubmit={(mode) => void handleAuthSubmit(mode)}
              profile={profile}
              onSeedProfile={() => void saveOnboardingProfile()}
              onSignOut={() => void handleSignOut()}
              onRefresh={() => void refresh()}
            />
          ) : (
            <ChatWorkspace
              draft={draft}
              mode={chatMode}
              modelTier={chatModelTier}
              attachments={composerAttachments}
              messages={messages}
              isBootstrapping={isLoading && messages.length === 0}
              isSending={isSending}
              setDraft={setDraft}
              setMode={setChatMode}
              setModelTier={setChatModelTier}
              onAttachFiles={(files) => void handleComposerFiles(files)}
              onRemoveAttachment={removeComposerAttachment}
              onSend={handleSend}
              onStop={stopChatResponse}
            />
          )}
        </section>

        <ContextPanel
          activePage={activePage}
          profile={profile}
          memories={memories}
          latestResponse={latestAssistantResponse}
        />
      </div>
      <MobileDrawer
        activePage={activePage}
        activeSessionId={activeSessionId}
        isOpen={isMobileNavOpen}
        sessions={chatSessions}
        setActivePage={handleSelectPage}
        onClose={() => setIsMobileNavOpen(false)}
        onNewChat={startNewChat}
        onOpenSession={(sessionId) => void openChatSession(sessionId)}
        onDeleteSession={(sessionId) => void handleDeleteChatSession(sessionId)}
      />
      <MobileContextDrawer
        activePage={activePage}
        isOpen={isMobileContextOpen}
        latestResponse={latestAssistantResponse}
        memories={memories}
        onClose={() => setIsMobileContextOpen(false)}
        profile={profile}
      />
    </main>
  );
}

function splitOnboardingTerms(value: string): string[] {
  return Array.from(
    new Set(
      value
        .split(/[,\n]/)
        .map((term) => term.trim())
        .filter(Boolean),
    ),
  ).slice(0, 8);
}

function buildOnboardingMemoryText(draft: ProfileInput, interests: string[]): string {
  const interestText = interests.length ? interests.join(", ") : "미정";
  return [
    `온보딩 관심사: ${interestText}`,
    `목표: ${draft.goal.trim() || "미정"}`,
    `코딩 경험: ${draft.coding_level}`,
    `학습 선호: ${draft.preference}`,
    `활동 방식: ${draft.activity_style}`,
    `주간 가능 시간: ${draft.weekly_hours}시간`,
  ].join(". ");
}

function buildFirstQuestion(draft: ProfileInput, interests: string[]): string {
  const interestText = interests.length ? interests.join(", ") : "AI";
  const departmentText =
    draft.department === "ai"
      ? "인공지능학부"
      : draft.department === "software"
        ? "소프트웨어학부"
        : "소프트웨어융합대학";
  return `${departmentText} ${draft.grade}학년이고 ${interestText}에 관심 있어. ${draft.goal.trim() || "진로 준비"} 기준으로 이번 학기에 뭘 먼저 하면 좋을까?`;
}

function FullPageShell({ children }: { children: ReactNode }) {
  return (
    <main className="flex min-h-screen items-center justify-center bg-[#faf8f3] px-5 text-[#191817]">
      <div className="w-full max-w-[520px] rounded-xl border border-[#ded7cb] bg-[#fffdf8] p-6 shadow-sm">
        {children}
      </div>
    </main>
  );
}

function DataLoadErrorPage({
  error,
  onRefresh,
  onSignOut,
}: {
  error: string;
  onRefresh: () => void;
  onSignOut: () => void;
}) {
  return (
    <FullPageShell>
      <div className="space-y-5">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#938d83]">
            KMU SW Navigator
          </p>
          <h1 className="mt-2 text-2xl font-semibold tracking-normal">정보를 불러오지 못했습니다</h1>
          <p className="mt-2 text-sm leading-6 text-[#716c63]">
            계정은 유지되어 있습니다. 잠시 후 다시 시도하거나 로그아웃한 뒤 다시 로그인해 주세요.
          </p>
        </div>
        <div className="rounded-lg border border-[#e3c8bd] bg-[#fff7f2] p-3 text-sm leading-6 text-[#9b3f24]">
          {error}
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            className="h-10 rounded-lg bg-[#191817] px-4 text-sm font-semibold text-[#fffdf8]"
            type="button"
            onClick={onRefresh}
          >
            다시 시도
          </button>
          <button
            className="inline-flex h-10 items-center gap-2 rounded-lg border border-[#c9c0b3] bg-[#fffdf8] px-4 text-sm font-semibold"
            type="button"
            onClick={onSignOut}
          >
            <LogOut className="h-4 w-4" aria-hidden="true" />
            로그아웃
          </button>
        </div>
      </div>
    </FullPageShell>
  );
}

function InlineDataLoadError({
  error,
  onRefresh,
  onSignOut,
}: {
  error: string;
  onRefresh: () => void;
  onSignOut: () => void;
}) {
  return (
    <section className="min-h-0 overflow-y-auto px-6 py-7">
      <div className="mx-auto max-w-[760px] rounded-xl border border-[#ded7cb] bg-[#fffdf8] p-5">
        <h2 className="text-xl font-semibold tracking-normal">정보를 다시 확인해야 합니다</h2>
        <p className="mt-2 text-sm leading-6 text-[#716c63]">
          계정 세션은 유지되어 있습니다. 현재 화면에서 바로 다시 시도할 수 있습니다.
        </p>
        <div className="mt-4 rounded-lg border border-[#e3c8bd] bg-[#fff7f2] p-3 text-sm leading-6 text-[#9b3f24]">
          {error}
        </div>
        <div className="mt-4 flex flex-wrap gap-2">
          <button
            className="h-10 rounded-lg bg-[#191817] px-4 text-sm font-semibold text-[#fffdf8]"
            type="button"
            onClick={onRefresh}
          >
            다시 시도
          </button>
          <button
            className="inline-flex h-10 items-center gap-2 rounded-lg border border-[#c9c0b3] bg-[#fffdf8] px-4 text-sm font-semibold"
            type="button"
            onClick={onSignOut}
          >
            <LogOut className="h-4 w-4" aria-hidden="true" />
            로그아웃
          </button>
        </div>
      </div>
    </section>
  );
}

function LoginPage({
  authMode,
  authEmail,
  authPassword,
  authStatus,
  isAuthBusy,
  setAuthMode,
  clearAuthStatus,
  setAuthEmail,
  setAuthPassword,
  onAuthSubmit,
}: {
  authMode: "signin" | "signup";
  authEmail: string;
  authPassword: string;
  authStatus: string | null;
  isAuthBusy: boolean;
  setAuthMode: (mode: "signin" | "signup") => void;
  clearAuthStatus: () => void;
  setAuthEmail: (value: string) => void;
  setAuthPassword: (value: string) => void;
  onAuthSubmit: (mode: "signin" | "signup") => void;
}) {
  const isSignup = authMode === "signup";
  return (
    <FullPageShell>
      <div className="space-y-5">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#938d83]">
            KMU SW Navigator
          </p>
          <h1 className="mt-2 text-2xl font-semibold tracking-normal">
            {isSignup ? "가입" : "로그인"}
          </h1>
          <p className="mt-2 text-sm leading-6 text-[#716c63]">
            {isSignup
              ? "계정을 만들고 나에게 맞는 상담, 추천, 일정 관리를 시작합니다."
              : "국민대 소프트웨어융합대학 생활에 맞춘 상담, 추천, 일정 관리를 시작합니다."}
          </p>
        </div>
        <form
          className="grid gap-3"
          onSubmit={(event) => {
            event.preventDefault();
            onAuthSubmit(authMode);
          }}
        >
          <label className="space-y-1 text-xs font-semibold text-[#716c63]">
            이메일
            <input
              className="h-11 w-full rounded-lg border border-[#c9c0b3] bg-[#fffdf8] px-3 text-sm font-normal text-[#191817] outline-none"
              type="email"
              value={authEmail}
              onChange={(event) => setAuthEmail(event.target.value)}
            />
          </label>
          <label className="space-y-1 text-xs font-semibold text-[#716c63]">
            비밀번호
            <input
              className="h-11 w-full rounded-lg border border-[#c9c0b3] bg-[#fffdf8] px-3 text-sm font-normal text-[#191817] outline-none"
              type="password"
              value={authPassword}
              onChange={(event) => setAuthPassword(event.target.value)}
            />
          </label>
          <div className="flex flex-wrap gap-2">
            <button
              className="inline-flex h-10 items-center gap-2 rounded-lg bg-[#191817] px-4 text-sm font-semibold text-[#fffdf8] disabled:opacity-50"
              type="submit"
              disabled={isAuthBusy}
            >
              <LogIn className="h-4 w-4" aria-hidden="true" />
              {isSignup ? "가입하기" : "로그인"}
            </button>
            <button
              className="h-10 rounded-lg border border-[#c9c0b3] bg-[#fffdf8] px-4 text-sm font-semibold disabled:opacity-50"
              type="button"
              disabled={isAuthBusy}
              onClick={() => {
                clearAuthStatus();
                setAuthMode(isSignup ? "signin" : "signup");
              }}
            >
              {isSignup ? "로그인으로 돌아가기" : "가입 페이지로 이동"}
            </button>
          </div>
        </form>
        {authStatus ? <p className="text-xs leading-5 text-[#716c63]">{authStatus}</p> : null}
      </div>
    </FullPageShell>
  );
}

function OnboardingPage({
  authSession,
  draft,
  setDraft,
  onSave,
  onSignOut,
}: {
  authSession: AuthSessionSummary;
  draft: ProfileInput;
  setDraft: (value: ProfileInput) => void;
  onSave: () => void;
  onSignOut: () => void;
}) {
  return (
    <FullPageShell>
      <div className="space-y-5">
        <div>
          <p className="text-xs font-semibold text-[#938d83]">
            {authSession.email ?? authSession.userId}
          </p>
          <h1 className="mt-2 text-2xl font-semibold tracking-normal">처음 설정</h1>
          <p className="mt-2 text-sm leading-6 text-[#716c63]">
            상담과 추천에 사용할 기본 학업 정보를 알려주세요. 나중에 설정에서 바꿀 수 있습니다.
          </p>
        </div>
        <div className="grid gap-3">
          <label className="space-y-1 text-xs font-semibold text-[#716c63]">
            학부
            <select
              className="h-11 w-full rounded-lg border border-[#c9c0b3] bg-[#fffdf8] px-3 text-sm font-normal text-[#191817] outline-none"
              value={draft.department}
              onChange={(event) =>
                setDraft({ ...draft, department: event.target.value as Department })
              }
            >
              <option value="software">소프트웨어학부</option>
              <option value="ai">인공지능학부</option>
              <option value="other">기타</option>
              <option value="unknown">미정</option>
            </select>
          </label>
          <label className="space-y-1 text-xs font-semibold text-[#716c63]">
            학년
            <select
              className="h-11 w-full rounded-lg border border-[#c9c0b3] bg-[#fffdf8] px-3 text-sm font-normal text-[#191817] outline-none"
              value={draft.grade}
              onChange={(event) => setDraft({ ...draft, grade: Number(event.target.value) })}
            >
              <option value={1}>1학년</option>
              <option value={2}>2학년</option>
              <option value={3}>3학년</option>
              <option value={4}>4학년</option>
            </select>
          </label>
          <label className="space-y-1 text-xs font-semibold text-[#716c63]">
            적용 교과과정
            <select
              className="h-11 w-full rounded-lg border border-[#c9c0b3] bg-[#fffdf8] px-3 text-sm font-normal text-[#191817] outline-none"
              value={draft.curriculum_year}
              onChange={(event) =>
                setDraft({ ...draft, curriculum_year: event.target.value as CurriculumYear })
              }
            >
              <option value="2025">2025</option>
              <option value="2024">2024</option>
              <option value="2023">2023</option>
              <option value="unknown">미정</option>
            </select>
          </label>
          <label className="space-y-1 text-xs font-semibold text-[#716c63]">
            관심 분야
            <input
              className="h-11 w-full rounded-lg border border-[#c9c0b3] bg-[#fffdf8] px-3 text-sm font-normal text-[#191817] outline-none"
              value={draft.interests_text}
              onChange={(event) => setDraft({ ...draft, interests_text: event.target.value })}
              placeholder="AI, 백엔드, 데이터"
            />
          </label>
          <label className="space-y-1 text-xs font-semibold text-[#716c63]">
            목표
            <input
              className="h-11 w-full rounded-lg border border-[#c9c0b3] bg-[#fffdf8] px-3 text-sm font-normal text-[#191817] outline-none"
              value={draft.goal}
              onChange={(event) => setDraft({ ...draft, goal: event.target.value })}
              placeholder="AI 서비스 개발"
            />
          </label>
          <div className="grid gap-3 sm:grid-cols-2">
            <label className="space-y-1 text-xs font-semibold text-[#716c63]">
              코딩 경험
              <select
                className="h-11 w-full rounded-lg border border-[#c9c0b3] bg-[#fffdf8] px-3 text-sm font-normal text-[#191817] outline-none"
                value={draft.coding_level}
                onChange={(event) =>
                  setDraft({
                    ...draft,
                    coding_level: event.target.value as RecommendationInputContext["codingLevel"],
                  })
                }
              >
                <option value="beginner">초급</option>
                <option value="intermediate">중급</option>
                <option value="advanced">고급</option>
              </select>
            </label>
            <label className="space-y-1 text-xs font-semibold text-[#716c63]">
              학습 선호
              <select
                className="h-11 w-full rounded-lg border border-[#c9c0b3] bg-[#fffdf8] px-3 text-sm font-normal text-[#191817] outline-none"
                value={draft.preference}
                onChange={(event) =>
                  setDraft({
                    ...draft,
                    preference: event.target.value as RecommendationInputContext["preference"],
                  })
                }
              >
                <option value="project">프로젝트</option>
                <option value="lecture">강의</option>
                <option value="study">스터디</option>
                <option value="unknown">미정</option>
              </select>
            </label>
            <label className="space-y-1 text-xs font-semibold text-[#716c63]">
              활동 방식
              <select
                className="h-11 w-full rounded-lg border border-[#c9c0b3] bg-[#fffdf8] px-3 text-sm font-normal text-[#191817] outline-none"
                value={draft.activity_style}
                onChange={(event) =>
                  setDraft({
                    ...draft,
                    activity_style: event.target.value as RecommendationInputContext["activityStyle"],
                  })
                }
              >
                <option value="team">팀</option>
                <option value="solo">개인</option>
                <option value="mixed">혼합</option>
                <option value="unknown">미정</option>
              </select>
            </label>
            <label className="space-y-1 text-xs font-semibold text-[#716c63]">
              주간 가능 시간
              <input
                className="h-11 w-full rounded-lg border border-[#c9c0b3] bg-[#fffdf8] px-3 text-sm font-normal text-[#191817] outline-none"
                min={0}
                max={40}
                type="number"
                value={draft.weekly_hours}
                onChange={(event) =>
                  setDraft({
                    ...draft,
                    weekly_hours: Math.min(Math.max(Number(event.target.value) || 0, 0), 40),
                  })
                }
              />
            </label>
          </div>
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            className="h-10 rounded-lg bg-[#191817] px-4 text-sm font-semibold text-[#fffdf8]"
            type="button"
            onClick={onSave}
          >
            시작하기
          </button>
          <button
            className="h-10 rounded-lg border border-[#c9c0b3] bg-[#fffdf8] px-4 text-sm font-semibold"
            type="button"
            onClick={onSignOut}
          >
            로그아웃
          </button>
        </div>
      </div>
    </FullPageShell>
  );
}

function ChatWorkspace({
  draft,
  mode,
  modelTier,
  attachments,
  messages,
  isBootstrapping,
  isSending,
  setDraft,
  setMode,
  setModelTier,
  onAttachFiles,
  onRemoveAttachment,
  onSend,
  onStop,
}: {
  draft: string;
  mode: ChatMode;
  modelTier: ChatModelTier;
  attachments: ComposerAttachment[];
  messages: ChatMessage[];
  isBootstrapping: boolean;
  isSending: boolean;
  setDraft: (value: string) => void;
  setMode: (value: ChatMode) => void;
  setModelTier: (value: ChatModelTier) => void;
  onAttachFiles: (files: FileList | null) => void;
  onRemoveAttachment: (attachmentId: string) => void;
  onSend: (event: FormEvent<HTMLFormElement>) => void;
  onStop: () => void;
}) {
  const scrollRef = useRef<HTMLElement | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [openMenu, setOpenMenu] = useState<"mode" | "model" | null>(null);
  const modeOptions: Array<{ value: ChatMode; label: string }> = [
    { value: "auto", label: "자동" },
    { value: "academic", label: "학업" },
    { value: "career", label: "진로" },
    { value: "schedule", label: "일정" },
  ];
  const modelTierOptions: Array<{ value: ChatModelTier; label: string }> = [
    { value: "balanced", label: "균형" },
    { value: "fast", label: "빠름" },
  ];

  useEffect(() => {
    const target = scrollRef.current;
    if (!target) {
      return;
    }
    target.scrollTo({ top: target.scrollHeight, behavior: "smooth" });
  }, [messages, isSending]);

  return (
    <div className="grid min-h-0 grid-rows-[minmax(0,1fr)_auto]">
      <section ref={scrollRef} className="min-h-0 overflow-y-auto px-5 py-7">
        <div className="mx-auto max-w-[820px] space-y-6">
          {isBootstrapping ? <ChatHistorySkeleton /> : null}
          {!isBootstrapping && messages.length === 0 ? (
            <ChatEmptyState setDraft={setDraft} />
          ) : null}
          {messages.map((message) => (
            <MessageBubble key={message.id} message={message} setDraft={setDraft} />
          ))}
        </div>
      </section>

      <form className="border-t border-[#ded7cb] px-5 py-4" onSubmit={onSend}>
        <div className="mx-auto max-w-[820px] rounded-xl border border-[#c9c0b3] bg-[#fffdf8] p-2">
          {attachments.length ? (
            <div className="mb-2 flex flex-wrap gap-2 px-1">
              {attachments.map((attachment) => (
                <span
                  className="inline-flex min-h-8 max-w-full items-center gap-2 rounded-lg border border-[#ded7cb] bg-[#faf8f3] px-2.5 text-xs text-[#3d3b37]"
                  key={attachment.id}
                  title={attachment.text_content ? "본문을 이번 질문에 함께 보냅니다." : "파일명만 첨부됩니다."}
                >
                  <Paperclip className="h-3.5 w-3.5 shrink-0" aria-hidden="true" />
                  <span className="max-w-[220px] truncate">{attachment.name}</span>
                  <button
                    className="grid h-5 w-5 place-items-center rounded hover:bg-[#ebe4d8]"
                    type="button"
                    onClick={() => onRemoveAttachment(attachment.id)}
                    title="첨부 제거"
                  >
                    <X className="h-3.5 w-3.5" aria-hidden="true" />
                  </button>
                </span>
              ))}
            </div>
          ) : null}
          <textarea
            className="block min-h-[76px] w-full resize-none bg-transparent px-2 py-2 text-[15px] leading-6 text-[#191817] outline-none"
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            placeholder="예: AI 트랙을 준비하려면 이번 학기에 어떤 과목과 활동을 먼저 하면 좋을까?"
            aria-label="AI 상담 입력"
          />
          <div className="flex flex-wrap items-center justify-between gap-2 px-1 pb-1">
            <div className="flex min-w-0 flex-wrap items-center gap-2">
              <ComposerDropdown
                icon={<SlidersHorizontal className="h-3.5 w-3.5" aria-hidden="true" />}
                isOpen={openMenu === "mode"}
                label={modeOptions.find((item) => item.value === mode)?.label ?? "자동"}
                onToggle={() => setOpenMenu((current) => (current === "mode" ? null : "mode"))}
                options={modeOptions}
                title="상담 모드"
                value={mode}
                onChange={(value) => {
                  setMode(value);
                  setOpenMenu(null);
                }}
              />
              <ComposerDropdown
                isOpen={openMenu === "model"}
                label={
                  modelTier === "balanced"
                    ? "균형 · Gemini 3 Flash"
                    : "빠름 · Flash-Lite"
                }
                onToggle={() => setOpenMenu((current) => (current === "model" ? null : "model"))}
                options={modelTierOptions}
                title="응답 품질"
                value={modelTier}
                onChange={(value) => {
                  setModelTier(value);
                  setOpenMenu(null);
                }}
              />
              <input
                ref={fileInputRef}
                className="hidden"
                type="file"
                multiple
                accept=".txt,.md,.csv,.json,.py,.ts,.tsx,.js,.jsx,.html,.css,text/*,application/json"
                onChange={(event) => {
                  onAttachFiles(event.target.files);
                  event.target.value = "";
                }}
              />
              <button
                className="inline-flex min-h-8 items-center gap-1.5 rounded-lg border border-[#ded7cb] bg-[#faf8f3] px-2.5 text-xs font-semibold text-[#3d3b37] disabled:opacity-50"
                type="button"
                disabled={attachments.length >= 3 || isSending}
                onClick={() => fileInputRef.current?.click()}
                title="파일 첨부"
              >
                <Paperclip className="h-3.5 w-3.5" aria-hidden="true" />
                파일
              </button>
            </div>
            <button
              className="grid h-9 w-9 place-items-center rounded-lg bg-[#191817] text-[#fffdf8] disabled:opacity-50"
              type={isSending ? "button" : "submit"}
              disabled={!isSending && !draft.trim()}
              onClick={isSending ? onStop : undefined}
              title={isSending ? "답변 중지" : "전송"}
            >
              {isSending ? (
                <Square className="h-4 w-4 fill-current" aria-hidden="true" />
              ) : (
                <Send className="h-4 w-4" aria-hidden="true" />
              )}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}

function ComposerDropdown<TValue extends string>({
  icon,
  isOpen,
  label,
  onChange,
  onToggle,
  options,
  title,
  value,
}: {
  icon?: ReactNode;
  isOpen: boolean;
  label: string;
  onChange: (value: TValue) => void;
  onToggle: () => void;
  options: Array<{ value: TValue; label: string }>;
  title: string;
  value: TValue;
}) {
  return (
    <div className="relative">
      <button
        className="inline-flex min-h-8 items-center gap-1.5 rounded-lg border border-[#ded7cb] bg-[#faf8f3] px-2.5 text-xs font-semibold text-[#3d3b37] hover:border-[#b8ad9f] hover:bg-[#f4efe6]"
        type="button"
        aria-expanded={isOpen}
        title={title}
        onClick={onToggle}
      >
        {icon}
        <span>{label}</span>
        <ChevronDown className="h-3.5 w-3.5 text-[#716c63]" aria-hidden="true" />
      </button>
      {isOpen ? (
        <div className="absolute bottom-[calc(100%+6px)] left-0 z-30 min-w-full overflow-hidden rounded-lg border border-[#c9c0b3] bg-[#fffdf8] p-1 shadow-lg">
          {options.map((item) => (
            <button
              className={`flex min-h-8 w-full items-center whitespace-nowrap rounded-md px-2.5 text-left text-xs font-semibold ${
                value === item.value
                  ? "bg-[#191817] text-[#fffdf8]"
                  : "text-[#3d3b37] hover:bg-[#f1ede5]"
              }`}
              key={item.value}
              type="button"
              onClick={() => onChange(item.value)}
            >
              {item.label}
            </button>
          ))}
        </div>
      ) : null}
    </div>
  );
}

function ChatEmptyState({ setDraft }: { setDraft: (value: string) => void }) {
  const starterPrompts = [
    {
      title: "수강신청 상담",
      description: "관심 분야와 학년 기준으로 먼저 볼 과목을 정리합니다.",
      prompt: "수강신청 전에 AI 트랙 기준으로 어떤 과목을 먼저 보면 좋을까?",
    },
    {
      title: "진로 준비",
      description: "백엔드, AI, 데이터 등 목표 직무별 준비 순서를 잡습니다.",
      prompt: "AI 서비스 개발과 백엔드에 관심 있어. 이번 학기에 포트폴리오로 뭘 준비하면 좋을까?",
    },
    {
      title: "일정 정리",
      description: "과제, 시험, 신청 마감 문장을 내부 일정으로 바꿉니다.",
      prompt: "캡스톤 회의는 금요일 오후 3시, 자료구조 과제는 다음 주 월요일까지야. 일정으로 정리해줘.",
    },
  ];

  return (
    <div className="rounded-2xl border border-[#ded7cb] bg-[#fffdf8] p-5 shadow-sm">
      <div className="flex items-start gap-3">
        <div className="grid h-10 w-10 shrink-0 place-items-center rounded-xl border border-[#ded7cb] bg-[#faf8f3] text-[#3d3b37]">
          <Lightbulb className="h-5 w-5" aria-hidden="true" />
        </div>
        <div className="min-w-0">
          <h2 className="text-lg font-semibold tracking-normal">무엇을 상담할까요?</h2>
          <p className="mt-1 text-sm leading-6 text-[#716c63]">
            예시를 누르면 입력창에 질문이 들어갑니다. 그대로 보내거나 내 상황에 맞게 고쳐서 보내세요.
          </p>
        </div>
      </div>
      <div className="mt-4 grid gap-2 md:grid-cols-3">
        {starterPrompts.map((item) => (
          <button
            className="rounded-xl border border-[#ded7cb] bg-[#faf8f3] p-4 text-left hover:border-[#b8ad9f] hover:bg-[#f4efe6]"
            key={item.title}
            type="button"
            onClick={() => setDraft(item.prompt)}
          >
            <span className="block text-sm font-semibold text-[#191817]">{item.title}</span>
            <span className="mt-1 block text-xs leading-5 text-[#716c63]">{item.description}</span>
            <span className="mt-3 inline-flex items-center gap-1 text-xs font-semibold text-[#3d3b37]">
              질문 넣기
              <ChevronRight className="h-3.5 w-3.5" aria-hidden="true" />
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}

function ChatHistorySkeleton() {
  return (
    <div className="space-y-5" aria-label="상담 기록 동기화 중">
      <div className="max-w-[640px] space-y-3 py-1">
        <div className="h-4 w-3/5 rounded bg-[#ebe4d8]" />
        <div className="h-4 w-5/6 rounded bg-[#f1ede5]" />
        <div className="h-4 w-2/3 rounded bg-[#f1ede5]" />
      </div>
      <div className="flex justify-end opacity-70">
        <div className="w-[min(620px,88%)] rounded-2xl border border-[#ded7cb] bg-[#fffdf8] px-4 py-3">
          <div className="h-4 w-3/5 rounded bg-[#ebe4d8]" />
        </div>
      </div>
    </div>
  );
}

function MessageBubble({
  message,
  setDraft,
}: {
  message: ChatMessage;
  setDraft: (value: string) => void;
}) {
  const isUser = message.role === "user";
  const sources = message.response ? buildSourceSummaries(message.response) : [];
  const isAssistantDone = !isUser && Boolean(message.response);
  const isAssistantWriting = !isUser && !message.isPending && message.text && !message.response;
  return (
    <article className={isUser ? "flex justify-end" : "flex justify-start"}>
      <div
        className={
          isUser
            ? "w-fit max-w-[min(720px,88%)] rounded-2xl border border-[#ded7cb] bg-[#fffdf8] px-4 py-3 text-[15px] leading-7 shadow-sm"
            : "max-w-[min(720px,100%)] py-1 text-[15px] leading-7"
        }
      >
        {isUser ? (
          <p>{message.text}</p>
        ) : message.isPending ? (
          <div className="inline-flex items-center gap-2 rounded-full border border-[#ded7cb] bg-[#fffdf8] px-3 py-2 text-sm text-[#716c63]">
            <span className="h-2 w-2 animate-pulse rounded-full bg-[#938d83]" />
            답변을 준비하고 있습니다
          </div>
        ) : (
          <Streamdown
            className="assistant-markdown"
            mode="static"
            plugins={{ cjk }}
          >
            {normalizeAssistantMarkdown(message.text)}
          </Streamdown>
        )}
        {isAssistantDone || isAssistantWriting ? (
          <div className="mt-3 flex flex-wrap items-center gap-2 text-xs text-[#716c63]">
            {isAssistantDone ? (
              <span
                className="inline-flex min-h-7 items-center gap-1.5 rounded-full border border-[#c7d8c4] bg-[#f3f8f0] px-3 text-[#3c6b35]"
                title={message.response?.model ?? "기본 응답"}
              >
                <CheckCircle2 className="h-3.5 w-3.5" aria-hidden="true" />
                {message.response?.model ? "Gemini 답변" : "답변 완료"}
              </span>
            ) : (
              <span className="inline-flex min-h-7 items-center gap-1.5 rounded-full border border-[#ded7cb] bg-[#fffdf8] px-3">
                <span className="h-2 w-2 animate-pulse rounded-full bg-[#938d83]" />
                답변 작성 중
              </span>
            )}
          </div>
        ) : null}
        {sources.length ? <SourceReferenceStrip sources={sources} /> : null}
        {message.response?.choices.length ? (
          <div className="mt-3">
            <p className="mb-2 text-xs font-semibold text-[#716c63]">이어서 물어볼 수 있는 질문</p>
            <div className="flex flex-wrap gap-2">
              {message.response.choices.map((choice, index) => (
                <button
                  className="inline-flex min-h-8 items-center gap-1 rounded-full border border-[#ded7cb] bg-[#fffdf8] px-3 text-xs text-[#3d3b37]"
                  key={`${choice.id}-${index}`}
                  type="button"
                  onClick={() => setDraft(choice.message)}
                  title="후속 질문을 입력창에 넣기"
                >
                  {choice.label}
                  <ChevronRight className="h-3.5 w-3.5" aria-hidden="true" />
                </button>
              ))}
            </div>
          </div>
        ) : null}
      </div>
    </article>
  );
}

interface SourceSummary {
  index: number;
  title: string;
  label: string;
  detail: string | null;
}

function normalizeAssistantMarkdown(text: string): string {
  const normalized = text
    .replace(/\\\*\\\*/g, "**")
    .replace(/\\_\\_/g, "__");
  const markerCount = (normalized.match(/\*\*/g) ?? []).length;
  return markerCount % 2 === 0 ? normalized : normalized.replace(/\*\*$/, "").replace(/\*\*/g, "");
}

function buildSourceSummaries(response: ChatResponse): SourceSummary[] {
  const seen = new Set<string>();
  const rawSources = [
    ...response.evidence.internal_sources.map((source) => ({ source, label: "학교 자료" })),
    ...response.evidence.web_sources.map((source) => ({ source, label: "웹 자료" })),
  ];

  return rawSources.flatMap(({ source, label }) => {
    const title = sourceTitle(source);
    const key = `${label}:${title}`;
    if (seen.has(key)) {
      return [];
    }
    seen.add(key);
    return [
      {
        index: seen.size,
        title,
        label,
        detail: sourceDetail(source),
      },
    ];
  }).slice(0, 4);
}

function sourceTitle(source: Record<string, unknown>): string {
  const title = String(source.title ?? source.heading_path ?? source.uri ?? "").trim();
  return title || "학교 자료";
}

function sourceDetail(source: Record<string, unknown>): string | null {
  const heading = String(source.heading_path ?? source.section ?? "").trim();
  const uri = String(source.uri ?? "").trim();
  if (heading && heading !== sourceTitle(source)) {
    return heading;
  }
  return uri || null;
}

function SourceReferenceStrip({ sources }: { sources: SourceSummary[] }) {
  return (
    <div className="mt-4 rounded-xl border border-[#ded7cb] bg-[#fffdf8] p-3">
      <div className="mb-2 flex items-center justify-between gap-3">
        <span className="text-xs font-semibold text-[#716c63]">답변 근거</span>
        <span className="text-[11px] text-[#938d83]">{sources.length}개 자료</span>
      </div>
      <div className="flex flex-wrap gap-2">
        {sources.map((source) => (
          <span
            className="inline-flex min-h-8 max-w-full items-center gap-2 rounded-lg border border-[#ded7cb] bg-[#faf8f3] px-2.5 text-xs text-[#3d3b37]"
            key={`${source.label}-${source.title}-${source.index}`}
            title={source.detail ?? source.title}
          >
            <span className="grid h-5 min-w-5 place-items-center rounded bg-[#191817] px-1 text-[11px] font-semibold text-[#fffdf8]">
              {source.index}
            </span>
            <span className="truncate">
              {source.label} · {source.title}
            </span>
          </span>
        ))}
      </div>
    </div>
  );
}

function ContextPanel({
  activePage,
  profile,
  memories,
  latestResponse,
}: {
  activePage: WorkspacePage;
  profile: Profile | MissingProfile | null;
  memories: Memory[];
  latestResponse?: ChatResponse;
}) {
  return (
    <aside className="hidden min-w-0 overflow-y-auto border-l border-[#ded7cb] bg-[#f7f2ea] p-3.5 lg:block">
      <ContextPanelContent
        activePage={activePage}
        latestResponse={latestResponse}
        memories={memories}
        profile={profile}
      />
    </aside>
  );
}

function MobileContextDrawer({
  activePage,
  isOpen,
  latestResponse,
  memories,
  onClose,
  profile,
}: {
  activePage: WorkspacePage;
  isOpen: boolean;
  latestResponse?: ChatResponse;
  memories: Memory[];
  onClose: () => void;
  profile: Profile | MissingProfile | null;
}) {
  if (!isOpen) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-40 lg:hidden" role="dialog" aria-modal="true">
      <button
        className="absolute inset-0 bg-[#191817]/30"
        type="button"
        aria-label="참고 정보 닫기"
        onClick={onClose}
      />
      <aside className="absolute right-0 z-10 h-full w-[min(340px,90vw)] overflow-y-auto border-l border-[#ded7cb] bg-[#f7f2ea] p-3.5 shadow-xl">
        <div className="mb-3 flex items-center justify-between gap-3">
          <div>
            <strong className="block text-sm font-semibold">참고 정보</strong>
            <span className="block text-xs text-[#716c63]">내 정보와 답변 근거</span>
          </div>
          <button
            className="grid h-9 w-9 place-items-center rounded-lg border border-[#c9c0b3] bg-[#fffdf8]"
            type="button"
            aria-label="참고 정보 닫기"
            onClick={onClose}
          >
            <X className="h-4 w-4" aria-hidden="true" />
          </button>
        </div>
        <ContextPanelContent
          activePage={activePage}
          latestResponse={latestResponse}
          memories={memories}
          profile={profile}
        />
      </aside>
    </div>
  );
}

function ContextPanelContent({
  activePage,
  profile,
  memories,
  latestResponse,
}: {
  activePage: WorkspacePage;
  profile: Profile | MissingProfile | null;
  memories: Memory[];
  latestResponse?: ChatResponse;
}) {
  const profileSummary = useMemo(() => {
    if (!profile?.exists) {
      return null;
    }
    return [
      ["소속", profile.department],
      ["학년", `${profile.grade}학년`],
      ["교과과정", profile.curriculum_year],
      ["관심", memories[0]?.natural_text ?? "미설정"],
    ];
  }, [profile, memories]);
  const panelSources = latestResponse ? buildSourceSummaries(latestResponse) : [];

  return (
    <>
      <Panel title="내 정보">
        {profileSummary ? (
          <div className="grid grid-cols-2 gap-2">
            {profileSummary.map(([label, value]) => (
              <div className="rounded-lg bg-[#f1ede5] p-2.5" key={label}>
                <span className="block text-[11px] text-[#716c63]">{label}</span>
                <strong className="mt-1 block truncate text-xs font-semibold">{value}</strong>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-xs leading-5 text-[#716c63]">
            설정에서 기본 정보를 저장하면 상담에 반영됩니다.
          </p>
        )}
      </Panel>

      <Panel title="관심 정보">
        {memories.length ? (
          <ul className="list-disc space-y-1 pl-4 text-xs leading-5 text-[#3d3b37]">
            {memories.map((memory) => (
              <li key={memory.id}>{memory.natural_text}</li>
            ))}
          </ul>
        ) : (
          <p className="text-xs leading-5 text-[#716c63]">아직 저장된 관심 정보가 없습니다.</p>
        )}
      </Panel>

      <Panel title={activePage === "chat" ? "답변 근거" : "참고 자료"}>
        {panelSources.length ? (
          <div className="space-y-2">
            {panelSources.map((source) => (
              <SourceCard
                key={`panel-source-${source.index}-${source.label}-${source.title}`}
                label={`[${source.index}] ${source.label}`}
                title={source.title}
              />
            ))}
          </div>
        ) : (
          <>
            <SourceCard label="학교 자료" title="소프트웨어학부 트랙 안내" />
            <SourceCard label="학교 자료" title="신입생 수강신청 안내" />
          </>
        )}
      </Panel>

      <Panel title="다음 행동">
        <p className="text-xs leading-5 text-[#716c63]">
          상담을 진행하면 답변에서 이어서 할 수 있는 질문과 일정 후보가 표시됩니다.
        </p>
      </Panel>
    </>
  );
}

function Panel({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="mb-3 rounded-xl border border-[#ded7cb] bg-[#fffdf8] p-3">
      <h2 className="mb-2.5 text-sm font-semibold tracking-normal">{title}</h2>
      {children}
    </section>
  );
}

function SourceCard({ label, title }: { label: string; title: string }) {
  return (
    <div className="rounded-lg bg-[#f1ede5] p-2.5">
      <span className="block text-[11px] text-[#716c63]">{label}</span>
      <strong className="mt-1 block text-xs font-semibold">{title}</strong>
    </div>
  );
}

function LogsPage({ logs }: { logs: LLMUsageLog[] }) {
  return (
    <section className="min-h-0 overflow-y-auto px-6 py-7">
      <div className="mx-auto max-w-[900px] rounded-xl border border-[#ded7cb] bg-[#fffdf8] p-5">
        <h2 className="text-xl font-semibold tracking-normal">상담 기록</h2>
        <p className="mt-2 text-sm leading-6 text-[#716c63]">
          AI 상담에서 어떤 도움을 받았는지 간단히 확인합니다.
        </p>
        <div className="mt-5 space-y-3">
          {logs.length ? (
            logs.slice(0, 10).map((log) => (
              <article className="rounded-lg bg-[#f1ede5] p-3" key={log.id}>
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <strong className="text-sm">{usageLogFeatureLabel(log.feature)}</strong>
                  <span className="text-xs text-[#716c63]">
                    {new Date(log.created_at).toLocaleDateString()}
                  </span>
                </div>
                <p className="mt-2 text-xs leading-5 text-[#3d3b37]">{log.purpose}</p>
                <p className="mt-1 line-clamp-2 text-xs leading-5 text-[#716c63]">
                  입력: {log.input_text}
                </p>
                {log.output_text ? (
                  <p className="mt-1 line-clamp-2 text-xs leading-5 text-[#716c63]">
                    출력: {log.output_text}
                  </p>
                ) : null}
              </article>
            ))
          ) : (
            <div className="rounded-lg bg-[#f1ede5] p-3 text-sm leading-6 text-[#716c63]">
              아직 상담 기록이 없습니다. AI 상담을 사용하면 이 화면에 기록됩니다.
            </div>
          )}
        </div>
      </div>
    </section>
  );
}

function usageLogFeatureLabel(feature: string): string {
  const labels: Record<string, string> = {
    rag_chat: "AI 상담",
    google_grounding: "진로 정보 보강",
    schedule_parser: "일정 정리",
    embedding_ingest: "자료 정리",
  };
  return labels[feature] ?? "상담 활동";
}

function SchedulePage({
  assignments,
  draft,
  preview,
  setDraft,
  onPreview,
  onSave,
  onComplete,
  onDelete,
}: {
  assignments: Assignment[];
  draft: string;
  preview: AssignmentPreview | null;
  setDraft: (value: string) => void;
  onPreview: () => void;
  onSave: () => void;
  onComplete: (assignmentId: string) => void;
  onDelete: (assignmentId: string) => void;
}) {
  return (
    <section className="min-h-0 overflow-y-auto px-6 py-7">
      <div className="mx-auto max-w-[900px] space-y-4">
        <div className="rounded-xl border border-[#ded7cb] bg-[#fffdf8] p-5">
          <h2 className="text-xl font-semibold tracking-normal">일정</h2>
          <div className="mt-4 rounded-xl border border-[#ded7cb] bg-[#faf8f3] p-3">
            <textarea
              className="block min-h-[72px] w-full resize-none bg-transparent text-sm leading-6 outline-none"
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              aria-label="일정 자연어 입력"
            />
            <div className="mt-3 flex flex-wrap gap-2">
              <button
                className="h-9 rounded-lg bg-[#191817] px-4 text-sm font-semibold text-[#fffdf8]"
                type="button"
                onClick={onPreview}
              >
                미리보기
              </button>
              <button
                className="h-9 rounded-lg border border-[#c9c0b3] bg-[#fffdf8] px-4 text-sm font-semibold disabled:opacity-50"
                type="button"
                disabled={!preview}
                onClick={onSave}
              >
                저장
              </button>
            </div>
          </div>
          {preview ? (
            <div className="mt-4 rounded-xl border border-[#ded7cb] bg-[#f1ede5] p-4">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h3 className="text-sm font-semibold">{preview.title}</h3>
                  <p className="mt-1 text-xs text-[#716c63]">
                    {preview.course ?? "과목 미지정"} · {new Date(preview.due_at).toLocaleDateString()}
                  </p>
                  <p className="mt-1 text-[11px] text-[#938d83]">
                    {preview.parser === "gemini" ? "자동 추출" : "기본 추출"}
                  </p>
                </div>
                <strong className="rounded-full bg-[#191817] px-3 py-1 text-xs text-[#fffdf8]">
                  {preview.d_day_label}
                </strong>
              </div>
            </div>
          ) : null}
        </div>

        <div className="grid gap-2">
          {assignments.map((assignment) => (
            <article
              className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-[#ded7cb] bg-[#fffdf8] p-4"
              key={assignment.id}
            >
              <div>
                <h3 className="text-sm font-semibold">{assignment.title}</h3>
                <p className="mt-1 text-xs text-[#716c63]">
                  {assignment.course ?? "과목 미지정"} · {new Date(assignment.due_at).toLocaleDateString()}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <strong className="text-sm">{assignment.d_day_label}</strong>
                <button
                  className="h-8 rounded-lg border border-[#c9c0b3] px-3 text-xs font-semibold"
                  type="button"
                  onClick={() => onComplete(assignment.id)}
                >
                  완료
                </button>
                <button
                  className="h-8 rounded-lg border border-[#c9c0b3] px-3 text-xs font-semibold text-[#716c63]"
                  type="button"
                  onClick={() => onDelete(assignment.id)}
                >
                  삭제
                </button>
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

function RecommendationPage({
  trackResult,
  activityResult,
  inputContext,
  inputDraft,
  isEdited,
  onRecommend,
  onResetInput,
  onUpdateInput,
}: {
  trackResult: TrackRecommendResponse | null;
  activityResult: ActivityRecommendResponse | null;
  inputContext: RecommendationInputContext;
  inputDraft: RecommendationInputDraft;
  isEdited: boolean;
  onRecommend: () => void;
  onResetInput: () => void;
  onUpdateInput: (patch: Partial<RecommendationInputDraft>) => void;
}) {
  return (
    <section className="min-h-0 overflow-y-auto px-6 py-7">
      <div className="mx-auto max-w-[920px] space-y-4">
        <div className="rounded-xl border border-[#ded7cb] bg-[#fffdf8] p-5">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <h2 className="text-xl font-semibold tracking-normal">진로/활동 추천</h2>
              <p className="mt-2 text-sm leading-6 text-[#716c63]">
                {inputContext.sourceLabel}를 바탕으로 지금 필요한 준비를 추천합니다.
              </p>
              <div className="mt-3 flex flex-wrap gap-2">
                {[...inputContext.trackInterests, inputContext.goal].slice(0, 5).map((item, index) => (
                  <EvidenceChip key={`input-context-${index}-${item}`} label={item} />
                ))}
              </div>
            </div>
            <button
              className="h-10 rounded-lg bg-[#191817] px-4 text-sm font-semibold text-[#fffdf8]"
              type="button"
              onClick={onRecommend}
            >
              추천 실행
            </button>
          </div>
          <div className="mt-5 grid gap-3 lg:grid-cols-2">
            <label className="space-y-1 text-xs font-semibold text-[#716c63]">
              트랙 관심사
              <input
                className="h-10 w-full rounded-lg border border-[#c9c0b3] bg-[#fffdf8] px-3 text-sm font-normal text-[#191817] outline-none"
                value={inputDraft.trackInterestsText}
                onChange={(event) => onUpdateInput({ trackInterestsText: event.target.value })}
                placeholder="AI, 백엔드"
              />
            </label>
            <label className="space-y-1 text-xs font-semibold text-[#716c63]">
              활동 관심사
              <input
                className="h-10 w-full rounded-lg border border-[#c9c0b3] bg-[#fffdf8] px-3 text-sm font-normal text-[#191817] outline-none"
                value={inputDraft.activityInterestsText}
                onChange={(event) => onUpdateInput({ activityInterestsText: event.target.value })}
                placeholder="개발, 알고리즘"
              />
            </label>
            <label className="space-y-1 text-xs font-semibold text-[#716c63] lg:col-span-2">
              목표
              <input
                className="h-10 w-full rounded-lg border border-[#c9c0b3] bg-[#fffdf8] px-3 text-sm font-normal text-[#191817] outline-none"
                value={inputDraft.goal}
                onChange={(event) => onUpdateInput({ goal: event.target.value })}
                placeholder="AI 서비스 개발"
              />
            </label>
            <label className="space-y-1 text-xs font-semibold text-[#716c63]">
              코딩 경험
              <select
                className="h-10 w-full rounded-lg border border-[#c9c0b3] bg-[#fffdf8] px-3 text-sm font-normal text-[#191817] outline-none"
                value={inputDraft.codingLevel}
                onChange={(event) =>
                  onUpdateInput({
                    codingLevel: event.target.value as RecommendationInputContext["codingLevel"],
                  })
                }
              >
                <option value="beginner">초급</option>
                <option value="intermediate">중급</option>
                <option value="advanced">고급</option>
              </select>
            </label>
            <label className="space-y-1 text-xs font-semibold text-[#716c63]">
              학습 선호
              <select
                className="h-10 w-full rounded-lg border border-[#c9c0b3] bg-[#fffdf8] px-3 text-sm font-normal text-[#191817] outline-none"
                value={inputDraft.preference}
                onChange={(event) =>
                  onUpdateInput({
                    preference: event.target.value as RecommendationInputContext["preference"],
                  })
                }
              >
                <option value="project">프로젝트</option>
                <option value="lecture">강의</option>
                <option value="study">스터디</option>
                <option value="unknown">미정</option>
              </select>
            </label>
            <label className="space-y-1 text-xs font-semibold text-[#716c63]">
              활동 방식
              <select
                className="h-10 w-full rounded-lg border border-[#c9c0b3] bg-[#fffdf8] px-3 text-sm font-normal text-[#191817] outline-none"
                value={inputDraft.activityStyle}
                onChange={(event) =>
                  onUpdateInput({
                    activityStyle: event.target.value as RecommendationInputContext["activityStyle"],
                  })
                }
              >
                <option value="team">팀</option>
                <option value="solo">개인</option>
                <option value="mixed">혼합</option>
                <option value="unknown">미정</option>
              </select>
            </label>
            <label className="space-y-1 text-xs font-semibold text-[#716c63]">
              주간 가능 시간
              <input
                className="h-10 w-full rounded-lg border border-[#c9c0b3] bg-[#fffdf8] px-3 text-sm font-normal text-[#191817] outline-none"
                min={0}
                max={40}
                type="number"
                value={inputDraft.weeklyHours}
                onChange={(event) => onUpdateInput({ weeklyHours: Number(event.target.value) })}
              />
            </label>
          </div>
          {isEdited ? (
            <button
              className="mt-4 h-9 rounded-lg border border-[#c9c0b3] bg-[#fffdf8] px-3 text-xs font-semibold text-[#3d3b37]"
              type="button"
              onClick={onResetInput}
            >
              자동값으로 되돌리기
            </button>
          ) : null}
        </div>

        <div className="grid gap-3 lg:grid-cols-2">
          <RecommendationPanel
            title="트랙 추천"
            items={trackResult?.recommendations ?? []}
            actions={trackResult?.recommended_actions ?? []}
            sources={trackResult?.evidence.internal_sources ?? []}
          />
          <RecommendationPanel
            title={activityResult?.activity_style ?? "활동 추천"}
            items={activityResult?.recommendations ?? []}
            actions={activityResult?.recommended_actions ?? []}
            sources={activityResult?.evidence.internal_sources ?? []}
          />
        </div>
      </div>
    </section>
  );
}

function RecommendationPanel({
  title,
  items,
  actions,
  sources,
}: {
  title: string;
  items: Array<{ id: string; title: string; score: number; reasons: string[] }>;
  actions: string[];
  sources: Array<Record<string, unknown>>;
}) {
  return (
    <div className="rounded-xl border border-[#ded7cb] bg-[#fffdf8] p-4">
      <h3 className="text-sm font-semibold">{title}</h3>
      <div className="mt-3 space-y-2">
        {items.length ? (
          items.slice(0, 3).map((item) => (
            <article className="rounded-lg bg-[#f1ede5] p-3" key={item.id}>
              <div className="flex items-center justify-between gap-3">
                <strong className="text-sm">{item.title}</strong>
                <span className="text-xs font-semibold text-[#716c63]">{item.score}점</span>
              </div>
              <p className="mt-2 text-xs leading-5 text-[#716c63]">{item.reasons[0]}</p>
            </article>
          ))
        ) : (
          <p className="text-xs leading-5 text-[#716c63]">추천 실행 후 결과가 표시됩니다.</p>
        )}
      </div>
      {actions.length ? (
        <ul className="mt-3 list-disc space-y-1 pl-4 text-xs leading-5 text-[#3d3b37]">
          {actions.slice(0, 3).map((action, index) => (
            <li key={`action-${index}-${action}`}>{action}</li>
          ))}
        </ul>
      ) : null}
      {sources.length ? (
        <div className="mt-3 flex flex-wrap gap-2">
          {sources.slice(0, 3).map((source, index) => (
            <EvidenceChip
              key={`recommendation-source-${index}-${String(source.title ?? "source")}-${String(source.heading_path ?? "")}`}
              label={`근거 · ${String(source.title ?? "내부 자료")}`}
            />
          ))}
        </div>
      ) : null}
    </div>
  );
}

function SettingsPage({
  authEmail,
  authPassword,
  authSession,
  authStatus,
  isAuthBusy,
  setAuthEmail,
  setAuthPassword,
  onAuthSubmit,
  profile,
  onSeedProfile,
  onSignOut,
  onRefresh,
}: {
  authEmail: string;
  authPassword: string;
  authSession: AuthSessionSummary | null;
  authStatus: string | null;
  isAuthBusy: boolean;
  setAuthEmail: (value: string) => void;
  setAuthPassword: (value: string) => void;
  onAuthSubmit: (mode: "signin" | "signup") => void;
  profile: Profile | MissingProfile | null;
  onSeedProfile: () => void;
  onSignOut: () => void;
  onRefresh: () => void;
}) {
  return (
    <section className="min-h-0 overflow-y-auto px-6 py-7">
      <div className="mx-auto max-w-[760px] rounded-xl border border-[#ded7cb] bg-[#fffdf8] p-5">
        <h2 className="text-xl font-semibold tracking-normal">설정</h2>
        <p className="mt-2 text-sm leading-6 text-[#716c63]">
          계정과 기본 학업 정보를 관리합니다.
        </p>
        <div className="mt-5 rounded-xl border border-[#ded7cb] bg-[#faf8f3] p-4">
          <h3 className="text-sm font-semibold">계정</h3>
          <p className="mt-1 text-xs leading-5 text-[#716c63]">
            {authSession
              ? `${authSession.email ?? authSession.userId} 계정으로 연결됨`
              : "로그인하면 상담과 일정이 계정에 저장됩니다."}
          </p>
          <div className="mt-3 grid gap-2 sm:grid-cols-2">
            <input
              className="h-10 rounded-lg border border-[#c9c0b3] bg-[#fffdf8] px-3 text-sm outline-none"
              type="email"
              placeholder="email"
              value={authEmail}
              onChange={(event) => setAuthEmail(event.target.value)}
            />
            <input
              className="h-10 rounded-lg border border-[#c9c0b3] bg-[#fffdf8] px-3 text-sm outline-none"
              type="password"
              placeholder="password"
              value={authPassword}
              onChange={(event) => setAuthPassword(event.target.value)}
            />
          </div>
          <div className="mt-3 flex flex-wrap gap-2">
            <button
              className="inline-flex h-10 items-center gap-2 rounded-lg bg-[#191817] px-4 text-sm font-semibold text-[#fffdf8] disabled:opacity-50"
              type="button"
              disabled={isAuthBusy}
              onClick={() => onAuthSubmit("signin")}
            >
              <LogIn className="h-4 w-4" aria-hidden="true" />
              로그인
            </button>
            <button
              className="h-10 rounded-lg border border-[#c9c0b3] bg-[#fffdf8] px-4 text-sm font-semibold disabled:opacity-50"
              type="button"
              disabled={isAuthBusy}
              onClick={() => onAuthSubmit("signup")}
            >
              가입
            </button>
            <button
              className="inline-flex h-10 items-center gap-2 rounded-lg border border-[#c9c0b3] bg-[#fffdf8] px-4 text-sm font-semibold disabled:opacity-50"
              type="button"
              disabled={isAuthBusy || !authSession}
              onClick={onSignOut}
            >
              <LogOut className="h-4 w-4" aria-hidden="true" />
              로그아웃
            </button>
          </div>
          {authStatus ? <p className="mt-3 text-xs leading-5 text-[#716c63]">{authStatus}</p> : null}
        </div>
        <div className="mt-5 flex flex-wrap gap-2">
          {!profile?.exists ? (
            <button
              className="h-10 rounded-lg bg-[#191817] px-4 text-sm font-semibold text-[#fffdf8]"
              type="button"
              onClick={onSeedProfile}
            >
              기본 정보 저장
            </button>
          ) : null}
          <button
            className="h-10 rounded-lg border border-[#c9c0b3] bg-[#fffdf8] px-4 text-sm font-semibold"
            type="button"
            onClick={onRefresh}
          >
            새로고침
          </button>
        </div>
      </div>
    </section>
  );
}

function EvidenceChip({ label }: { label: string }) {
  return (
    <span className="inline-flex min-h-7 items-center rounded-full border border-[#ded7cb] bg-[#fffdf8] px-3 text-xs text-[#716c63]">
      {label}
    </span>
  );
}

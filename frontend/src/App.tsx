import {
  ChevronRight,
  LogIn,
  LogOut,
  Send,
  X,
} from "lucide-react";
import { cjk } from "@streamdown/cjk";
import { FormEvent, type ReactNode, useEffect, useMemo, useState } from "react";
import { Streamdown } from "streamdown";
import { Toaster, toast } from "sonner";

import { Sidebar, MobileDrawer } from "./components/navigation";
import { TopBar } from "./components/TopBar";
import {
  ApiError,
  getChatMessages,
  getChatSessions,
  createAssignment,
  deleteAssignment,
  exportAssignmentToCalendar,
  getAssignments,
  getMemories,
  getGoogleCalendarConnectUrl,
  getGoogleCalendarStatus,
  getLLMUsageLogs,
  getProfile,
  getPublicRuntimeStatus,
  getRuntimeStatus,
  previewAssignment,
  recommendActivity,
  recommendTrack,
  sendChatMessage,
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
  pageDescription,
  pageTitle,
  placeholderCards,
  recommendationContextToDraft,
  recommendationDraftToContext,
} from "./lib/navigator";
import type {
  Assignment,
  ActivityRecommendResponse,
  AssignmentPreview,
  ChatResponse,
  ChatSessionSummary,
  GoogleCalendarStatus,
  LLMUsageLog,
  Memory,
  MissingProfile,
  Profile,
  RuntimeComponentStatus,
  RuntimeStatus,
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
    return "Supabase schema.sql이 아직 적용되지 않아 live 저장소를 사용할 수 없습니다.";
  }
  return error instanceof Error ? error.message : fallback;
}

interface ProfileInput {
  department: Department;
  grade: number;
  curriculum_year: CurriculumYear;
}

export default function App() {
  const [activePage, setActivePage] = useState<WorkspacePage>("chat");
  const [profile, setProfile] = useState<Profile | MissingProfile | null>(null);
  const [memories, setMemories] = useState<Memory[]>([]);
  const [chatSessions, setChatSessions] = useState<ChatSessionSummary[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [draft, setDraft] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthChecked, setIsAuthChecked] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [authSession, setAuthSession] = useState<AuthSessionSummary | null>(null);
  const [authEmail, setAuthEmail] = useState("");
  const [authPassword, setAuthPassword] = useState("");
  const [authStatus, setAuthStatus] = useState<string | null>(null);
  const [isAuthBusy, setIsAuthBusy] = useState(false);
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [assignmentDraft, setAssignmentDraft] = useState("자료구조 과제 다음주 금요일까지");
  const [assignmentPreview, setAssignmentPreview] = useState<AssignmentPreview | null>(null);
  const [googleCalendarStatus, setGoogleCalendarStatus] = useState<GoogleCalendarStatus | null>(null);
  const [runtimeStatus, setRuntimeStatus] = useState<RuntimeStatus | null>(null);
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
  });

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
        setGoogleCalendarStatus(null);
        setRuntimeStatus(null);
        return;
      }
      const [runtimeStatusResult, appDataResult] = await Promise.allSettled([
        getRuntimeStatus(),
        Promise.all([
          getProfile(),
          getMemories(),
          getChatSessions(),
          getGoogleCalendarStatus(),
          getLLMUsageLogs(),
        ]),
      ]);
      if (runtimeStatusResult.status === "fulfilled") {
        setRuntimeStatus(runtimeStatusResult.value);
      } else {
        setRuntimeStatus(null);
      }
      if (appDataResult.status === "rejected") {
        throw appDataResult.reason;
      }
      const [profileData, memoryData, sessionsData, calendarStatusData, llmLogData] =
        appDataResult.value;
      setProfile(profileData);
      setMemories(memoryData);
      setChatSessions(sessionsData);
      setGoogleCalendarStatus(calendarStatusData);
      setLlmUsageLogs(llmLogData);
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
    setIsAuthBusy(true);
    try {
      if (mode === "signin") {
        await signInWithEmailPassword(authEmail, authPassword);
        setAuthStatus("로그인되었습니다.");
        toast.success("로그인되었습니다.");
      } else {
        await signUpWithEmailPassword(authEmail, authPassword);
        setAuthStatus("가입 요청이 완료되었습니다. Supabase 설정에 따라 이메일 확인이 필요할 수 있습니다.");
        toast.success("가입 요청이 완료되었습니다.");
      }
      await refreshAuthSession();
      await refresh();
    } catch (authError) {
      const message = getErrorMessage(authError, "인증 요청에 실패했습니다.");
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
      setGoogleCalendarStatus(null);
      setRuntimeStatus(null);
      setMessages([]);
      setActiveSessionId(null);
      setAuthStatus("로그아웃되었습니다.");
      await refreshPublicRuntimeStatus();
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

  async function handleExportAssignment(assignmentId: string) {
    setError(null);
    try {
      const exported = await exportAssignmentToCalendar(assignmentId);
      setAssignments((current) =>
        current.map((assignment) =>
          assignment.id === assignmentId
            ? {
                ...assignment,
                calendar_event_id: exported.calendar_event_id,
                calendar_synced_at: exported.calendar_synced_at,
              }
            : assignment,
        ),
      );
      toast.success("Google Calendar에 일정을 내보냈습니다.");
    } catch (apiError) {
      const message = getErrorMessage(apiError, "Calendar 내보내기에 실패했습니다.");
      setError(message);
      toast.error(message);
    }
  }

  async function handleConnectGoogleCalendar() {
    setError(null);
    try {
      const response = await getGoogleCalendarConnectUrl();
      if (!response.authorization_url) {
        const message = response.reason ?? "Google Calendar OAuth 설정이 필요합니다.";
        setError(message);
        toast.error(message);
        return;
      }
      window.location.assign(response.authorization_url);
    } catch (apiError) {
      const message = getErrorMessage(apiError, "Calendar 연결 URL을 만들지 못했습니다.");
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

  async function saveOnboardingProfile() {
    setError(null);
    try {
      setProfile(
        await upsertProfile(onboardingDraft),
      );
      setActivePage("chat");
      toast.success("프로필을 저장했습니다.");
      await refresh();
    } catch (apiError) {
      const message = getErrorMessage(apiError, "프로필 저장에 실패했습니다.");
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
    setMessages((current) => [
      ...current,
      { id: `user-${Date.now()}`, role: "user", text: message },
    ]);

    try {
      const response = await sendChatMessage(message, activeSessionId);
      setActiveSessionId(response.session_id);
      void refreshChatSessions();
      setMessages((current) => [
        ...current,
        {
          id: `assistant-${Date.now()}`,
          role: "assistant",
          text: response.answer,
          response,
        },
      ]);
      toast.success("AI 답변을 받았습니다.");
    } catch (apiError) {
      const message = getErrorMessage(apiError, "채팅 요청에 실패했습니다.");
      setError(message);
      toast.error(message);
    } finally {
      setIsSending(false);
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
    try {
      const records = await getChatMessages(sessionId);
      setMessages(
        records.map((record) => ({
          id: record.id,
          role: record.role === "assistant" ? "assistant" : "user",
          text: record.content,
        })),
      );
    } catch (apiError) {
      const message = getErrorMessage(apiError, "채팅 기록을 불러오지 못했습니다.");
      setError(message);
      toast.error(message);
    }
  }

  function startNewChat() {
    setActivePage("chat");
    setIsMobileNavOpen(false);
    setActiveSessionId(null);
    setMessages([]);
    setDraft("수강신청 전에 AI 트랙 기준으로 어떤 과목을 볼까?");
  }

  function handleSelectPage(page: WorkspacePage) {
    setActivePage(page);
    setIsMobileNavOpen(false);
  }

  useEffect(() => {
    void refreshPublicRuntimeStatus();
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
        setLlmUsageLogs([]);
        setIsLoading(false);
      }
    });
    return () => {
      subscription?.data.subscription.unsubscribe();
    };
  }, []);

  async function refreshPublicRuntimeStatus() {
    try {
      setRuntimeStatus(await getPublicRuntimeStatus());
    } catch {
      setRuntimeStatus(null);
    }
  }

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
        authEmail={authEmail}
        authPassword={authPassword}
        authStatus={authStatus}
        isAuthBusy={isAuthBusy}
        setAuthEmail={setAuthEmail}
        setAuthPassword={setAuthPassword}
        onAuthSubmit={(mode) => void handleAuthSubmit(mode)}
        runtimeStatus={runtimeStatus}
      />
    );
  }

  if (!isLoading && profile === null && error) {
    return (
      <DataLoadErrorPage
        error={error}
        runtimeStatus={runtimeStatus}
        onRefresh={() => void refresh()}
        onSignOut={() => void handleSignOut()}
      />
    );
  }

  if (isLoading || profile === null) {
    return (
      <FullPageShell>
        <div className="text-sm font-semibold text-[#716c63]">사용자 데이터를 불러오는 중입니다.</div>
      </FullPageShell>
    );
  }

  if (!profile.exists) {
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
    <main className="h-screen min-h-[720px] overflow-hidden bg-[#faf8f3] text-[#191817]">
      <Toaster richColors position="top-right" />
      <div className="grid h-full grid-cols-1 lg:grid-cols-[272px_minmax(0,1fr)_336px]">
        <Sidebar
          activePage={activePage}
          sessions={chatSessions}
          setActivePage={handleSelectPage}
          onNewChat={startNewChat}
          onOpenSession={(sessionId) => void openChatSession(sessionId)}
        />

        <section className="grid min-w-0 grid-rows-[64px_minmax(0,1fr)] bg-[#faf8f3]">
          <TopBar
            activePage={activePage}
            authSession={authSession}
            error={error}
            isLoading={isLoading}
            onOpenMobileContext={() => setIsMobileContextOpen(true)}
            onRefresh={() => void refresh()}
            onOpenMobileNav={() => setIsMobileNavOpen(true)}
          />

          {activePage === "chat" ? (
            <ChatWorkspace
              draft={draft}
              messages={messages}
              isSending={isSending}
              setDraft={setDraft}
              onSend={handleSend}
            />
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
              onExport={(assignmentId) => void handleExportAssignment(assignmentId)}
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
              googleCalendarStatus={googleCalendarStatus}
              runtimeStatus={runtimeStatus}
              onSeedProfile={() => void saveOnboardingProfile()}
              onSignOut={() => void handleSignOut()}
              onRefresh={() => void refresh()}
              onConnectGoogleCalendar={() => void handleConnectGoogleCalendar()}
            />
          ) : (
            <WorkspacePlaceholder page={activePage} />
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
        isOpen={isMobileNavOpen}
        sessions={chatSessions}
        setActivePage={handleSelectPage}
        onClose={() => setIsMobileNavOpen(false)}
        onNewChat={startNewChat}
        onOpenSession={(sessionId) => void openChatSession(sessionId)}
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
  runtimeStatus,
  onRefresh,
  onSignOut,
}: {
  error: string;
  runtimeStatus: RuntimeStatus | null;
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
          <h1 className="mt-2 text-2xl font-semibold tracking-normal">
            Live 데이터 로딩 확인 필요
          </h1>
          <p className="mt-2 text-sm leading-6 text-[#716c63]">
            Supabase Auth 로그인은 유지됐지만 사용자별 저장소를 읽는 단계에서 문제가 발생했습니다.
          </p>
        </div>
        <div className="rounded-lg border border-[#e3c8bd] bg-[#fff7f2] p-3 text-sm leading-6 text-[#9b3f24]">
          {error}
        </div>
        <LiveStatusPanel runtimeStatus={runtimeStatus} showGoogleCalendar />
        <div className="flex flex-wrap gap-2">
          <button
            className="h-10 rounded-lg bg-[#191817] px-4 text-sm font-semibold text-[#fffdf8]"
            type="button"
            onClick={onRefresh}
          >
            상태 새로고침
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

function LoginPage({
  authEmail,
  authPassword,
  authStatus,
  isAuthBusy,
  setAuthEmail,
  setAuthPassword,
  onAuthSubmit,
  runtimeStatus,
}: {
  authEmail: string;
  authPassword: string;
  authStatus: string | null;
  isAuthBusy: boolean;
  setAuthEmail: (value: string) => void;
  setAuthPassword: (value: string) => void;
  onAuthSubmit: (mode: "signin" | "signup") => void;
  runtimeStatus: RuntimeStatus | null;
}) {
  return (
    <FullPageShell>
      <div className="space-y-5">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#938d83]">
            KMU SW Navigator
          </p>
          <h1 className="mt-2 text-2xl font-semibold tracking-normal">로그인</h1>
          <p className="mt-2 text-sm leading-6 text-[#716c63]">
            Supabase Auth 세션으로 로그인해야 학업 상담, 일정, 추천, LLM 기록을 사용할 수 있습니다.
          </p>
        </div>
        <div className="grid gap-3">
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
        </div>
        <div className="flex flex-wrap gap-2">
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
        </div>
        <LiveStatusPanel runtimeStatus={runtimeStatus} />
        {authStatus ? <p className="text-xs leading-5 text-[#716c63]">{authStatus}</p> : null}
      </div>
    </FullPageShell>
  );
}

function LiveStatusPanel({
  runtimeStatus,
  showGoogleCalendar = false,
}: {
  runtimeStatus: RuntimeStatus | null;
  showGoogleCalendar?: boolean;
}) {
  return (
    <div className="rounded-xl border border-[#ded7cb] bg-[#faf8f3] p-4">
      <h2 className="text-sm font-semibold">Live API 상태</h2>
      <div className="mt-3 grid gap-2">
        <RuntimeStatusRow
          label="Supabase backend"
          status={runtimeStatus?.supabase_backend}
          readyText="env 연결됨"
        />
        <RuntimeStatusRow
          label="Supabase schema"
          status={runtimeStatus?.supabase_schema}
          readyText="schema.sql 적용됨"
        />
        <RuntimeStatusRow label="Gemini" status={runtimeStatus?.gemini} readyText="API 키 연결됨" />
        {showGoogleCalendar ? (
          <RuntimeStatusRow
            label="Google Calendar"
            status={runtimeStatus?.google_calendar}
            readyText="OAuth env 연결됨"
          />
        ) : null}
      </div>
      {runtimeStatus?.supabase_schema.next_actions.length ? (
        <div className="mt-3 rounded-lg border border-[#e3c8bd] bg-[#fff7f2] p-3">
          <p className="text-xs font-semibold text-[#9b3f24]">Supabase schema 다음 액션</p>
          <ol className="mt-2 list-decimal space-y-1 pl-4 text-xs leading-5 text-[#716c63]">
            {runtimeStatus.supabase_schema.next_actions.map((action) => (
              <li key={action}>
                <code className="break-all rounded bg-[#fffdf8] px-1 py-0.5 text-[#191817]">
                  {action}
                </code>
              </li>
            ))}
          </ol>
        </div>
      ) : null}
      <RuntimeStatusDetails
        title="Supabase schema missing 항목"
        items={runtimeStatus?.supabase_schema.missing_schema}
      />
      {showGoogleCalendar ? (
        <RuntimeStatusDetails
          title="Google Calendar missing env"
          items={runtimeStatus?.google_calendar.missing_env}
        />
      ) : null}
    </div>
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
            상담과 추천에 사용할 기본 학업 정보를 저장합니다. 이 값은 Supabase의 현재 로그인 사용자 프로필에 저장됩니다.
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
  messages,
  isSending,
  setDraft,
  onSend,
}: {
  draft: string;
  messages: ChatMessage[];
  isSending: boolean;
  setDraft: (value: string) => void;
  onSend: (event: FormEvent<HTMLFormElement>) => void;
}) {
  return (
    <div className="grid min-h-0 grid-rows-[minmax(0,1fr)_auto]">
      <section className="min-h-0 overflow-y-auto px-5 py-7">
        <div className="mx-auto max-w-[820px] space-y-6">
          {messages.map((message) => (
            <MessageBubble key={message.id} message={message} setDraft={setDraft} />
          ))}
        </div>
      </section>

      <form className="border-t border-[#ded7cb] px-5 py-4" onSubmit={onSend}>
        <div className="mx-auto max-w-[820px] rounded-xl border border-[#c9c0b3] bg-[#fffdf8] p-2">
          <textarea
            className="block min-h-[76px] w-full resize-none bg-transparent px-2 py-2 text-[15px] leading-6 text-[#191817] outline-none"
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            aria-label="AI 상담 입력"
          />
          <div className="flex items-center justify-between gap-3">
            <div className="flex flex-wrap gap-2">
              {["학업", "진로", "일정 추출"].map((label) => (
                <button
                  className="min-h-7 rounded-full border border-[#ded7cb] bg-[#faf8f3] px-3 text-xs text-[#716c63]"
                  key={label}
                  type="button"
                >
                  {label}
                </button>
              ))}
            </div>
            <button
              className="grid h-9 w-9 place-items-center rounded-lg bg-[#191817] text-[#fffdf8] disabled:opacity-50"
              type="submit"
              disabled={isSending}
              title="전송"
            >
              <Send className="h-4 w-4" aria-hidden="true" />
            </button>
          </div>
        </div>
      </form>
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
  const evidence = message.response?.evidence;
  return (
    <article className="grid grid-cols-[32px_minmax(0,1fr)] gap-3">
      <div className="grid h-8 w-8 place-items-center rounded-lg border border-[#ded7cb] bg-[#fffdf8] text-xs font-bold text-[#716c63]">
        {isUser ? "나" : "AI"}
      </div>
      <div
        className={
          isUser
            ? "max-w-[720px] rounded-xl border border-[#ded7cb] bg-[#fffdf8] px-4 py-3 text-[15px] leading-7"
            : "max-w-[720px] py-1 text-[15px] leading-7"
        }
      >
        {isUser ? (
          <p>{message.text}</p>
        ) : (
          <Streamdown
            className="assistant-markdown"
            mode="static"
            plugins={{ cjk }}
          >
            {message.text}
          </Streamdown>
        )}
        {message.response ? (
          <div className="mt-3 flex flex-wrap gap-2">
            <EvidenceChip label={`intent · ${message.response.intent}`} />
            {evidence?.personalization.map((item) => (
              <EvidenceChip key={item} label={`개인화 · ${item}`} />
            ))}
            {evidence?.internal_sources.map((source) => (
              <EvidenceChip key={String(source.title)} label={`출처 · ${String(source.title)}`} />
            ))}
            {evidence?.web_sources.map((source) => (
              <EvidenceChip key={String(source.uri ?? source.title)} label={`웹 · ${String(source.title)}`} />
            ))}
          </div>
        ) : null}
        {message.response?.choices.length ? (
          <div className="mt-3 flex flex-wrap gap-2">
            {message.response.choices.map((choice) => (
              <button
                className="inline-flex min-h-8 items-center gap-1 rounded-full border border-[#ded7cb] bg-[#fffdf8] px-3 text-xs text-[#3d3b37]"
                key={choice.id}
                type="button"
                onClick={() => setDraft(choice.message)}
              >
                {choice.label}
                <ChevronRight className="h-3.5 w-3.5" aria-hidden="true" />
              </button>
            ))}
          </div>
        ) : null}
      </div>
    </article>
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
        aria-label="모바일 컨텍스트 닫기"
        onClick={onClose}
      />
      <aside className="absolute right-0 z-10 h-full w-[min(340px,90vw)] overflow-y-auto border-l border-[#ded7cb] bg-[#f7f2ea] p-3.5 shadow-xl">
        <div className="mb-3 flex items-center justify-between gap-3">
          <div>
            <strong className="block text-sm font-semibold">컨텍스트</strong>
            <span className="block text-xs text-[#716c63]">프로필, 메모리, 근거</span>
          </div>
          <button
            className="grid h-9 w-9 place-items-center rounded-lg border border-[#c9c0b3] bg-[#fffdf8]"
            type="button"
            aria-label="컨텍스트 닫기"
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

  return (
    <>
      <Panel title="현재 프로필">
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
            설정에서 기본 프로필을 저장하면 상담 근거로 사용됩니다.
          </p>
        )}
      </Panel>

      <Panel title="저장된 메모리">
        {memories.length ? (
          <ul className="list-disc space-y-1 pl-4 text-xs leading-5 text-[#3d3b37]">
            {memories.map((memory) => (
              <li key={memory.id}>{memory.natural_text}</li>
            ))}
          </ul>
        ) : (
          <p className="text-xs leading-5 text-[#716c63]">아직 활성 메모리가 없습니다.</p>
        )}
      </Panel>

      <Panel title={activePage === "chat" ? "답변 근거" : "페이지 컨텍스트"}>
        {latestResponse?.evidence.internal_sources.length || latestResponse?.evidence.web_sources.length ? (
          <div className="space-y-2">
            {latestResponse?.evidence.internal_sources.map((source) => (
              <SourceCard
                key={String(source.title)}
                label={String(source.status ?? "internal")}
                title={String(source.title ?? "내부 자료")}
              />
            ))}
            {latestResponse?.evidence.web_sources.map((source) => (
              <SourceCard
                key={String(source.uri ?? source.title)}
                label="web"
                title={String(source.title ?? "웹 근거")}
              />
            ))}
          </div>
        ) : (
          <>
            <SourceCard label="Mini Wiki" title="소프트웨어학부 트랙 안내" />
            <SourceCard label="Mini Wiki" title="신입생 수강신청 안내" />
          </>
        )}
      </Panel>

      <Panel title="다가오는 일정">
        <p className="text-xs leading-5 text-[#3d3b37]">D-3 자료구조 과제</p>
        <p className="text-xs leading-5 text-[#3d3b37]">D-8 동아리 지원 마감</p>
      </Panel>

      <Panel title="추천 액션">
        <ul className="list-disc space-y-1 pl-4 text-xs leading-5 text-[#3d3b37]">
          <li>Python 기초 로드맵 저장</li>
          <li>AI 관련 동아리 후보 저장</li>
          <li>다음 주 과제 일정 추출</li>
        </ul>
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

function WorkspacePlaceholder({ page }: { page: WorkspacePage }) {
  const title = pageTitle(page);
  const cards = placeholderCards(page);
  return (
    <section className="min-h-0 overflow-y-auto px-6 py-7">
      <div className="mx-auto max-w-[920px]">
        <p className="text-xs font-bold uppercase tracking-[0.08em] text-[#938d83]">workspace</p>
        <h2 className="mt-2 text-2xl font-semibold tracking-normal">{title}</h2>
        <p className="mt-2 max-w-2xl text-sm leading-6 text-[#716c63]">
          이 화면은 다음 구현 slice에서 실제 API와 연결됩니다. 지금은 전체 앱 내비게이션과
          페이지 전환 구조를 먼저 고정합니다.
        </p>
        <div className="mt-6 grid gap-3 md:grid-cols-3">
          {cards.map((card) => (
            <article className="rounded-xl border border-[#ded7cb] bg-[#fffdf8] p-4" key={card.title}>
              <h3 className="text-sm font-semibold">{card.title}</h3>
              <p className="mt-2 text-xs leading-5 text-[#716c63]">{card.description}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

function LogsPage({ logs }: { logs: LLMUsageLog[] }) {
  return (
    <section className="min-h-0 overflow-y-auto px-6 py-7">
      <div className="mx-auto max-w-[900px] rounded-xl border border-[#ded7cb] bg-[#fffdf8] p-5">
        <h2 className="text-xl font-semibold tracking-normal">LLM 활용 기록</h2>
        <p className="mt-2 text-sm leading-6 text-[#716c63]">
          앱 내부 Gemini 호출 기록과 제출용 문서 기록을 함께 확인합니다.
        </p>
        <div className="mt-5 space-y-3">
          {logs.length ? (
            logs.slice(0, 10).map((log) => (
              <article className="rounded-lg bg-[#f1ede5] p-3" key={log.id}>
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <strong className="text-sm">{log.feature}</strong>
                  <span className="text-xs text-[#716c63]">{log.model ?? "local"}</span>
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
              아직 앱 내부 LLM 호출 기록이 없습니다. Gemini key가 있는 상태로 채팅 답변을
              생성하면 이 화면에 기록됩니다.
            </div>
          )}
        </div>
      </div>
    </section>
  );
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
  onExport,
}: {
  assignments: Assignment[];
  draft: string;
  preview: AssignmentPreview | null;
  setDraft: (value: string) => void;
  onPreview: () => void;
  onSave: () => void;
  onComplete: (assignmentId: string) => void;
  onDelete: (assignmentId: string) => void;
  onExport: (assignmentId: string) => void;
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
                    {preview.parser === "gemini" ? "Gemini parser" : "Python rules"}
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
                  className="h-8 rounded-lg border border-[#c9c0b3] px-3 text-xs font-semibold disabled:opacity-50"
                  type="button"
                  disabled={Boolean(assignment.calendar_event_id)}
                  onClick={() => onExport(assignment.id)}
                >
                  {assignment.calendar_event_id ? "Calendar 완료" : "Calendar"}
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
                {inputContext.sourceLabel} 기준으로 Python 추천 규칙을 실행합니다.
              </p>
              <div className="mt-3 flex flex-wrap gap-2">
                {[...inputContext.trackInterests, inputContext.goal].slice(0, 5).map((item) => (
                  <EvidenceChip key={item} label={item} />
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
          {actions.slice(0, 3).map((action) => (
            <li key={action}>{action}</li>
          ))}
        </ul>
      ) : null}
      {sources.length ? (
        <div className="mt-3 flex flex-wrap gap-2">
          {sources.slice(0, 3).map((source) => (
            <EvidenceChip
              key={`${String(source.title ?? "source")}-${String(source.heading_path ?? "")}`}
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
  googleCalendarStatus,
  runtimeStatus,
  onSeedProfile,
  onSignOut,
  onRefresh,
  onConnectGoogleCalendar,
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
  googleCalendarStatus: GoogleCalendarStatus | null;
  runtimeStatus: RuntimeStatus | null;
  onSeedProfile: () => void;
  onSignOut: () => void;
  onRefresh: () => void;
  onConnectGoogleCalendar: () => void;
}) {
  return (
    <section className="min-h-0 overflow-y-auto px-6 py-7">
      <div className="mx-auto max-w-[760px] rounded-xl border border-[#ded7cb] bg-[#fffdf8] p-5">
        <h2 className="text-xl font-semibold tracking-normal">설정</h2>
        <p className="mt-2 text-sm leading-6 text-[#716c63]">
          프로필, 메모리, API live 연결 상태를 관리하는 화면입니다.
        </p>
        <div className="mt-5">
          <LiveStatusPanel runtimeStatus={runtimeStatus} showGoogleCalendar />
        </div>
        <div className="mt-5 rounded-xl border border-[#ded7cb] bg-[#faf8f3] p-4">
          <h3 className="text-sm font-semibold">Supabase 로그인</h3>
          <p className="mt-1 text-xs leading-5 text-[#716c63]">
            {authSession
              ? `${authSession.email ?? authSession.userId} 계정으로 연결됨`
              : "Supabase env와 계정이 있으면 실제 세션으로 API를 호출합니다."}
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
        <div className="mt-5 rounded-xl border border-[#ded7cb] bg-[#faf8f3] p-4">
          <h3 className="text-sm font-semibold">Google Calendar</h3>
          <p className="mt-1 text-xs leading-5 text-[#716c63]">
            {googleCalendarStatus?.configured
              ? "OAuth 설정이 감지되었습니다. 연결하면 일정 내보내기에 실제 Google consent를 사용할 수 있습니다."
              : "GOOGLE_OAUTH_CLIENT_ID / SECRET 설정 후 실제 Calendar consent를 사용할 수 있습니다."}
          </p>
          <div className="mt-3 flex flex-wrap items-center gap-2">
            <span className="rounded-full border border-[#ded7cb] bg-[#fffdf8] px-3 py-1 text-xs font-semibold text-[#716c63]">
              {googleCalendarStatus?.connected ? "connected" : "not connected"}
            </span>
            <button
              className="h-10 rounded-lg border border-[#c9c0b3] bg-[#fffdf8] px-4 text-sm font-semibold disabled:opacity-50"
              type="button"
              disabled={!googleCalendarStatus?.configured}
              onClick={onConnectGoogleCalendar}
            >
              Calendar 연결
            </button>
          </div>
        </div>
        <div className="mt-5 flex flex-wrap gap-2">
          {!profile?.exists ? (
            <button
              className="h-10 rounded-lg bg-[#191817] px-4 text-sm font-semibold text-[#fffdf8]"
              type="button"
              onClick={onSeedProfile}
            >
              기본 프로필 저장
            </button>
          ) : null}
          <button
            className="h-10 rounded-lg border border-[#c9c0b3] bg-[#fffdf8] px-4 text-sm font-semibold"
            type="button"
            onClick={onRefresh}
          >
            상태 새로고침
          </button>
        </div>
      </div>
    </section>
  );
}

function RuntimeStatusRow({
  label,
  status,
  readyText,
}: {
  label: string;
  status?: RuntimeComponentStatus | null;
  readyText: string;
}) {
  const problemItems = status ? [...status.missing_env, ...status.missing_schema] : [];
  const hiddenCount = Math.max(problemItems.length - 3, 0);
  const detail = status?.ready
    ? readyText
    : problemItems.length
      ? `${problemItems.slice(0, 3).join(", ")}${hiddenCount ? ` 외 ${hiddenCount}개` : ""}`
      : status?.blocker ?? "확인 전";

  return (
    <div className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-[#ded7cb] bg-[#fffdf8] px-3 py-2">
      <span className="text-xs font-semibold text-[#191817]">{label}</span>
      <span className="text-xs text-[#716c63]">{detail}</span>
      <span
        className={`rounded-full px-2 py-1 text-[11px] font-semibold ${
          status?.ready ? "bg-[#dff1df] text-[#1f6b36]" : "bg-[#f8e1d8] text-[#9b3f24]"
        }`}
      >
        {status?.ready ? "live" : "blocked"}
      </span>
    </div>
  );
}

function RuntimeStatusDetails({
  title,
  items,
}: {
  title: string;
  items?: string[] | null;
}) {
  if (!items?.length) {
    return null;
  }

  return (
    <div className="mt-3 rounded-lg border border-[#ded7cb] bg-[#fffdf8] p-3">
      <p className="text-xs font-semibold text-[#716c63]">{title}</p>
      <div className="mt-2 flex max-h-32 flex-wrap gap-1 overflow-y-auto">
        {items.map((item) => (
          <code
            className="rounded border border-[#ded7cb] bg-[#faf8f3] px-2 py-1 text-[11px] text-[#191817]"
            key={item}
          >
            {item}
          </code>
        ))}
      </div>
    </div>
  );
}

function EvidenceChip({ label }: { label: string }) {
  return (
    <span className="inline-flex min-h-7 items-center rounded-full border border-[#ded7cb] bg-[#fffdf8] px-3 text-xs text-[#716c63]">
      {label}
    </span>
  );
}

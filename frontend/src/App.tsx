import {
  BookOpen,
  BriefcaseBusiness,
  CalendarDays,
  ChevronRight,
  ClipboardList,
  FolderKanban,
  LogIn,
  LogOut,
  Menu,
  MessageSquareText,
  PanelRight,
  RefreshCw,
  Send,
  Settings,
  X,
} from "lucide-react";
import { FormEvent, useEffect, useMemo, useState } from "react";

import {
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
  TrackRecommendResponse,
} from "./types/api";

type WorkspacePage = "chat" | "roadmap" | "career" | "project" | "schedule" | "logs" | "settings";

interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  text: string;
  response?: ChatResponse;
}

interface RecommendationInputContext {
  trackInterests: string[];
  activityInterests: string[];
  goal: string;
  codingLevel: "beginner" | "intermediate" | "advanced";
  preference: "lecture" | "project" | "study" | "unknown";
  activityStyle: "solo" | "team" | "mixed" | "unknown";
  weeklyHours: number;
  sourceLabel: string;
}

interface RecommendationInputDraft {
  trackInterestsText: string;
  activityInterestsText: string;
  goal: string;
  codingLevel: RecommendationInputContext["codingLevel"];
  preference: RecommendationInputContext["preference"];
  activityStyle: RecommendationInputContext["activityStyle"];
  weeklyHours: number;
}

const workspaceItems: Array<{
  id: WorkspacePage;
  label: string;
  count: number;
  icon: typeof MessageSquareText;
}> = [
  { id: "chat", label: "AI 상담", count: 12, icon: MessageSquareText },
  { id: "roadmap", label: "학업 로드맵", count: 4, icon: BookOpen },
  { id: "career", label: "진로/취업", count: 3, icon: BriefcaseBusiness },
  { id: "project", label: "프로젝트", count: 2, icon: FolderKanban },
  { id: "schedule", label: "일정", count: 6, icon: CalendarDays },
];

export default function App() {
  const [activePage, setActivePage] = useState<WorkspacePage>("chat");
  const [profile, setProfile] = useState<Profile | MissingProfile | null>(null);
  const [memories, setMemories] = useState<Memory[]>([]);
  const [chatSessions, setChatSessions] = useState<ChatSessionSummary[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "seed-user",
      role: "user",
      text: "AI 쪽 관심 있는데 1학년 때 뭘 먼저 보면 좋아?",
    },
    {
      id: "seed-assistant",
      role: "assistant",
      text: "지금 프로필 기준으로는 Python 기초, 자료구조, 수학/통계 기초를 먼저 잡고, 2학기부터 작은 AI 프로젝트를 하나 만드는 흐름이 좋습니다.",
    },
  ]);
  const [draft, setDraft] = useState("수강신청 전에 AI 트랙 기준으로 어떤 과목을 볼까?");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
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
  const [llmUsageLogs, setLlmUsageLogs] = useState<LLMUsageLog[]>([]);
  const [trackResult, setTrackResult] = useState<TrackRecommendResponse | null>(null);
  const [activityResult, setActivityResult] = useState<ActivityRecommendResponse | null>(null);
  const [isMobileNavOpen, setIsMobileNavOpen] = useState(false);
  const [isMobileContextOpen, setIsMobileContextOpen] = useState(false);
  const [isRecommendationEdited, setIsRecommendationEdited] = useState(false);

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
      const [profileData, memoryData, sessionsData, calendarStatusData, llmLogData] = await Promise.all([
        getProfile(),
        getMemories(),
        getChatSessions(),
        getGoogleCalendarStatus(),
        getLLMUsageLogs(),
      ]);
      setProfile(profileData);
      setMemories(memoryData);
      setChatSessions(sessionsData);
      setGoogleCalendarStatus(calendarStatusData);
      setLlmUsageLogs(llmLogData);
      setAssignments(await getAssignments());
    } catch (apiError) {
      setError(apiError instanceof Error ? apiError.message : "데이터를 불러오지 못했습니다.");
    } finally {
      setIsLoading(false);
    }
  }

  async function refreshAuthSession() {
    setAuthSession(await getAuthSession());
  }

  async function handleAuthSubmit(mode: "signin" | "signup") {
    setAuthStatus(null);
    setError(null);
    setIsAuthBusy(true);
    try {
      if (mode === "signin") {
        await signInWithEmailPassword(authEmail, authPassword);
        setAuthStatus("로그인되었습니다.");
      } else {
        await signUpWithEmailPassword(authEmail, authPassword);
        setAuthStatus("가입 요청이 완료되었습니다. Supabase 설정에 따라 이메일 확인이 필요할 수 있습니다.");
      }
      await refreshAuthSession();
      await refresh();
    } catch (authError) {
      setAuthStatus(authError instanceof Error ? authError.message : "인증 요청에 실패했습니다.");
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
      setAuthStatus("로그아웃되었습니다. demo fallback으로 전환됩니다.");
      await refresh();
    } catch (authError) {
      setAuthStatus(authError instanceof Error ? authError.message : "로그아웃에 실패했습니다.");
    } finally {
      setIsAuthBusy(false);
    }
  }

  async function handlePreviewAssignment() {
    setError(null);
    try {
      setAssignmentPreview(await previewAssignment(assignmentDraft));
    } catch (apiError) {
      setError(apiError instanceof Error ? apiError.message : "일정 미리보기에 실패했습니다.");
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
    } catch (apiError) {
      setError(apiError instanceof Error ? apiError.message : "일정 저장에 실패했습니다.");
    }
  }

  async function handleCompleteAssignment(assignmentId: string) {
    setError(null);
    try {
      const updated = await updateAssignment(assignmentId, { status: "done" });
      setAssignments((current) => current.filter((assignment) => assignment.id !== updated.id));
    } catch (apiError) {
      setError(apiError instanceof Error ? apiError.message : "일정 완료 처리에 실패했습니다.");
    }
  }

  async function handleDeleteAssignment(assignmentId: string) {
    setError(null);
    try {
      await deleteAssignment(assignmentId);
      setAssignments((current) => current.filter((assignment) => assignment.id !== assignmentId));
    } catch (apiError) {
      setError(apiError instanceof Error ? apiError.message : "일정 삭제에 실패했습니다.");
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
    } catch (apiError) {
      setError(apiError instanceof Error ? apiError.message : "Calendar 내보내기에 실패했습니다.");
    }
  }

  async function handleConnectGoogleCalendar() {
    setError(null);
    try {
      const response = await getGoogleCalendarConnectUrl();
      if (!response.authorization_url) {
        setError(response.reason ?? "Google Calendar OAuth 설정이 필요합니다.");
        return;
      }
      window.location.assign(response.authorization_url);
    } catch (apiError) {
      setError(apiError instanceof Error ? apiError.message : "Calendar 연결 URL을 만들지 못했습니다.");
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
    } catch (apiError) {
      setError(apiError instanceof Error ? apiError.message : "추천 요청에 실패했습니다.");
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

  async function seedProfile() {
    setError(null);
    try {
      setProfile(
        await upsertProfile({
          department: "software",
          grade: 1,
          curriculum_year: "2025",
        }),
      );
    } catch (apiError) {
      setError(apiError instanceof Error ? apiError.message : "프로필 저장에 실패했습니다.");
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
    } catch (apiError) {
      setError(apiError instanceof Error ? apiError.message : "채팅 요청에 실패했습니다.");
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
      setError(apiError instanceof Error ? apiError.message : "채팅 기록을 불러오지 못했습니다.");
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
    void refresh();
  }, []);

  useEffect(() => {
    void refreshAuthSession();
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
      void refresh();
    });
    return () => {
      subscription?.data.subscription.unsubscribe();
    };
  }, []);

  return (
    <main className="h-screen min-h-[720px] overflow-hidden bg-[#faf8f3] text-[#191817]">
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
              onSeedProfile={() => void seedProfile()}
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

function Sidebar({
  activePage,
  sessions,
  setActivePage,
  onNewChat,
  onOpenSession,
}: {
  activePage: WorkspacePage;
  sessions: ChatSessionSummary[];
  setActivePage: (page: WorkspacePage) => void;
  onNewChat: () => void;
  onOpenSession: (sessionId: string) => void;
}) {
  return (
    <aside className="hidden min-w-0 border-r border-[#ded7cb] bg-[#f1ede5] p-3 lg:block">
      <div className="flex items-center gap-3 px-2 pb-4 pt-1">
        <div className="grid h-8 w-8 place-items-center rounded-lg border border-[#c9c0b3] bg-[#fffdf8] text-sm font-bold">
          K
        </div>
        <div>
          <strong className="block text-sm font-semibold tracking-normal">SW Navigator</strong>
          <span className="block text-xs text-[#716c63]">personal campus AI</span>
        </div>
      </div>

      <button
        className="h-10 w-full rounded-lg bg-[#191817] text-sm font-semibold text-[#fffdf8]"
        type="button"
        onClick={onNewChat}
      >
        새 상담
      </button>

      <SidebarLabel>Workspace</SidebarLabel>
      <div className="space-y-1">
        {workspaceItems.map((item) => {
          const Icon = item.icon;
          const selected = activePage === item.id;
          return (
            <button
              className={`flex min-h-9 w-full items-center justify-between rounded-lg px-2.5 text-sm ${
                selected
                  ? "border border-[#ded7cb] bg-[#fffdf8] text-[#191817]"
                  : "text-[#3d3b37] hover:bg-[#f7f2ea]"
              }`}
              key={item.id}
              type="button"
              onClick={() => setActivePage(item.id)}
            >
              <span className="flex items-center gap-2">
                <Icon className="h-4 w-4" aria-hidden="true" />
                {item.label}
              </span>
              <span className="text-xs text-[#938d83]">{item.count}</span>
            </button>
          );
        })}
      </div>

      <SidebarLabel>Recent chats</SidebarLabel>
      <div className="space-y-1">
        {(sessions.length
          ? sessions
          : [
              {
                id: "sample-1",
                title: "AI 트랙을 어떻게 준비할까?",
                intent: "학업/진로",
              },
              {
                id: "sample-2",
                title: "자료구조 과제 마감 정리",
                intent: "일정",
              },
            ]
        ).map((chat, index) => (
          <button
            className={`w-full rounded-lg px-2.5 py-2 text-left ${
              index === 0 ? "border border-[#ded7cb] bg-[#fffdf8]" : "hover:bg-[#f7f2ea]"
            }`}
            key={chat.id}
            type="button"
            onClick={() => (sessions.length ? onOpenSession(chat.id) : setActivePage("chat"))}
          >
            <strong className="block truncate text-sm font-semibold">{chat.title ?? "새 상담"}</strong>
            <span className="mt-1 block text-xs text-[#716c63]">
              {chat.intent ?? "general"}
            </span>
          </button>
        ))}
      </div>

      <div className="absolute bottom-3 left-3 right-auto hidden w-[248px] space-y-1 lg:block">
        <button
          className="flex h-9 w-full items-center gap-2 rounded-lg px-2.5 text-sm text-[#3d3b37] hover:bg-[#f7f2ea]"
          type="button"
          onClick={() => setActivePage("logs")}
        >
          <ClipboardList className="h-4 w-4" aria-hidden="true" />
          LLM 기록
        </button>
        <button
          className="flex h-9 w-full items-center gap-2 rounded-lg px-2.5 text-sm text-[#3d3b37] hover:bg-[#f7f2ea]"
          type="button"
          onClick={() => setActivePage("settings")}
        >
          <Settings className="h-4 w-4" aria-hidden="true" />
          설정
        </button>
      </div>
    </aside>
  );
}

function MobileDrawer({
  activePage,
  isOpen,
  sessions,
  setActivePage,
  onClose,
  onNewChat,
  onOpenSession,
}: {
  activePage: WorkspacePage;
  isOpen: boolean;
  sessions: ChatSessionSummary[];
  setActivePage: (page: WorkspacePage) => void;
  onClose: () => void;
  onNewChat: () => void;
  onOpenSession: (sessionId: string) => void;
}) {
  if (!isOpen) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-40 lg:hidden" role="dialog" aria-modal="true">
      <button
        className="absolute inset-0 bg-[#191817]/30"
        type="button"
        aria-label="모바일 메뉴 닫기"
        onClick={onClose}
      />
      <aside className="relative z-10 flex h-full w-[min(320px,88vw)] flex-col border-r border-[#ded7cb] bg-[#f1ede5] p-3 shadow-xl">
        <div className="flex items-center justify-between gap-3 px-2 pb-4 pt-1">
          <div className="flex min-w-0 items-center gap-3">
            <div className="grid h-8 w-8 shrink-0 place-items-center rounded-lg border border-[#c9c0b3] bg-[#fffdf8] text-sm font-bold">
              K
            </div>
            <div className="min-w-0">
              <strong className="block truncate text-sm font-semibold tracking-normal">
                SW Navigator
              </strong>
              <span className="block truncate text-xs text-[#716c63]">personal campus AI</span>
            </div>
          </div>
          <button
            className="grid h-9 w-9 place-items-center rounded-lg border border-[#c9c0b3] bg-[#fffdf8]"
            type="button"
            aria-label="메뉴 닫기"
            onClick={onClose}
          >
            <X className="h-4 w-4" aria-hidden="true" />
          </button>
        </div>

        <button
          className="h-10 w-full rounded-lg bg-[#191817] text-sm font-semibold text-[#fffdf8]"
          type="button"
          onClick={onNewChat}
        >
          새 상담
        </button>

        <div className="min-h-0 flex-1 overflow-y-auto">
          <SidebarLabel>Workspace</SidebarLabel>
          <div className="space-y-1">
            {workspaceItems.map((item) => {
              const Icon = item.icon;
              const selected = activePage === item.id;
              return (
                <button
                  className={`flex min-h-10 w-full items-center justify-between rounded-lg px-2.5 text-sm ${
                    selected
                      ? "border border-[#ded7cb] bg-[#fffdf8] text-[#191817]"
                      : "text-[#3d3b37] hover:bg-[#f7f2ea]"
                  }`}
                  key={item.id}
                  type="button"
                  onClick={() => setActivePage(item.id)}
                >
                  <span className="flex items-center gap-2">
                    <Icon className="h-4 w-4" aria-hidden="true" />
                    {item.label}
                  </span>
                  <span className="text-xs text-[#938d83]">{item.count}</span>
                </button>
              );
            })}
          </div>

          <SidebarLabel>Recent chats</SidebarLabel>
          <div className="space-y-1">
            {(sessions.length
              ? sessions
              : [
                  {
                    id: "sample-1",
                    title: "AI 트랙을 어떻게 준비할까?",
                    intent: "학업/진로",
                  },
                  {
                    id: "sample-2",
                    title: "자료구조 과제 마감 정리",
                    intent: "일정",
                  },
                ]
            ).map((chat, index) => (
              <button
                className={`w-full rounded-lg px-2.5 py-2 text-left ${
                  index === 0 ? "border border-[#ded7cb] bg-[#fffdf8]" : "hover:bg-[#f7f2ea]"
                }`}
                key={chat.id}
                type="button"
                onClick={() => (sessions.length ? onOpenSession(chat.id) : setActivePage("chat"))}
              >
                <strong className="block truncate text-sm font-semibold">
                  {chat.title ?? "새 상담"}
                </strong>
                <span className="mt-1 block text-xs text-[#716c63]">
                  {chat.intent ?? "general"}
                </span>
              </button>
            ))}
          </div>
        </div>

        <div className="border-t border-[#ded7cb] pt-2">
          <button
            className="flex h-10 w-full items-center gap-2 rounded-lg px-2.5 text-sm text-[#3d3b37] hover:bg-[#f7f2ea]"
            type="button"
            onClick={() => setActivePage("logs")}
          >
            <ClipboardList className="h-4 w-4" aria-hidden="true" />
            LLM 기록
          </button>
          <button
            className="flex h-10 w-full items-center gap-2 rounded-lg px-2.5 text-sm text-[#3d3b37] hover:bg-[#f7f2ea]"
            type="button"
            onClick={() => setActivePage("settings")}
          >
            <Settings className="h-4 w-4" aria-hidden="true" />
            설정
          </button>
        </div>
      </aside>
    </div>
  );
}

function SidebarLabel({ children }: { children: string }) {
  return (
    <p className="mb-2 ml-2 mt-5 text-[11px] font-bold uppercase tracking-[0.06em] text-[#938d83]">
      {children}
    </p>
  );
}

function TopBar({
  activePage,
  authSession,
  error,
  isLoading,
  onOpenMobileContext,
  onOpenMobileNav,
  onRefresh,
}: {
  activePage: WorkspacePage;
  authSession: AuthSessionSummary | null;
  error: string | null;
  isLoading: boolean;
  onOpenMobileContext: () => void;
  onOpenMobileNav: () => void;
  onRefresh: () => void;
}) {
  const title = pageTitle(activePage);
  return (
    <header className="flex min-w-0 items-center justify-between gap-4 border-b border-[#ded7cb] px-5">
      <div className="flex min-w-0 items-center gap-3">
        <button
          className="grid h-9 w-9 shrink-0 place-items-center rounded-lg border border-[#c9c0b3] bg-[#fffdf8] lg:hidden"
          type="button"
          aria-label="모바일 메뉴 열기"
          onClick={onOpenMobileNav}
        >
          <Menu className="h-4 w-4" aria-hidden="true" />
        </button>
        <div className="min-w-0">
        <h1 className="truncate text-[17px] font-semibold tracking-normal">{title}</h1>
        <p className="mt-1 truncate text-xs text-[#716c63]">
          {error ?? (isLoading ? "프로필과 메모리를 불러오는 중" : pageDescription(activePage))}
        </p>
        </div>
      </div>
      <div className="flex items-center gap-2">
        <span className="hidden rounded-full border border-[#ded7cb] bg-[#fffdf8] px-3 py-1 text-xs font-semibold text-[#716c63] md:inline-flex">
          {authSession ? "Supabase session" : "demo user"}
        </span>
        <button
          className="hidden h-9 items-center gap-2 rounded-lg border border-[#c9c0b3] bg-[#fffdf8] px-3 text-xs font-semibold text-[#3d3b37] sm:inline-flex"
          type="button"
          onClick={onRefresh}
        >
          <RefreshCw className="h-4 w-4" aria-hidden="true" />
          새로고침
        </button>
        <button
          className="grid h-9 w-9 place-items-center rounded-lg border border-[#c9c0b3] bg-[#fffdf8] lg:hidden"
          type="button"
          aria-label="모바일 컨텍스트 열기"
          onClick={onOpenMobileContext}
        >
          <PanelRight className="h-4 w-4" aria-hidden="true" />
        </button>
      </div>
    </header>
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
        <p>{message.text}</p>
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
          프로필, 메모리, Calendar 연동 상태를 관리하는 화면입니다.
        </p>
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

function EvidenceChip({ label }: { label: string }) {
  return (
    <span className="inline-flex min-h-7 items-center rounded-full border border-[#ded7cb] bg-[#fffdf8] px-3 text-xs text-[#716c63]">
      {label}
    </span>
  );
}

function buildRecommendationInputContext(memories: Memory[]): RecommendationInputContext {
  const memoryText = memories
    .map((memory) => `${memory.natural_text} ${Object.values(memory.value_json).join(" ")}`)
    .join(" ");
  const interests = deriveInterestKeywords(memoryText);

  return {
    trackInterests: interests.track.length ? interests.track : ["AI", "백엔드"],
    activityInterests: interests.activity.length ? interests.activity : ["개발", "운동"],
    goal: deriveGoal(memoryText),
    codingLevel: deriveCodingLevel(memoryText),
    preference: deriveLearningPreference(memoryText),
    activityStyle: deriveActivityStyle(memoryText),
    weeklyHours: deriveWeeklyHours(memoryText),
    sourceLabel: memories.length ? "프로필/메모리" : "데모 fallback",
  };
}

function recommendationContextToDraft(context: RecommendationInputContext): RecommendationInputDraft {
  return {
    trackInterestsText: context.trackInterests.join(", "),
    activityInterestsText: context.activityInterests.join(", "),
    goal: context.goal,
    codingLevel: context.codingLevel,
    preference: context.preference,
    activityStyle: context.activityStyle,
    weeklyHours: context.weeklyHours,
  };
}

function recommendationDraftToContext(
  draft: RecommendationInputDraft,
  sourceLabel: string,
): RecommendationInputContext {
  return {
    trackInterests: splitRecommendationTerms(draft.trackInterestsText, ["AI", "백엔드"]),
    activityInterests: splitRecommendationTerms(draft.activityInterestsText, ["개발", "운동"]),
    goal: draft.goal.trim() || "AI 서비스 개발",
    codingLevel: draft.codingLevel,
    preference: draft.preference,
    activityStyle: draft.activityStyle,
    weeklyHours: Math.min(Math.max(Number(draft.weeklyHours) || 0, 0), 40),
    sourceLabel,
  };
}

function splitRecommendationTerms(value: string, fallback: string[]): string[] {
  const terms = value
    .split(/[,\n]/)
    .map((term) => term.trim())
    .filter(Boolean);

  return terms.length ? Array.from(new Set(terms)).slice(0, 8) : fallback;
}

function deriveInterestKeywords(text: string): { track: string[]; activity: string[] } {
  const normalized = text.toLowerCase();
  const trackRules = [
    ["AI", ["ai", "인공지능", "머신러닝", "llm"]],
    ["백엔드", ["백엔드", "backend", "api", "서버"]],
    ["프론트엔드", ["프론트", "frontend", "react", "웹"]],
    ["창업", ["창업", "스타트업", "mvp"]],
    ["데이터", ["데이터", "database", "db", "분석"]],
  ] as const;
  const activityRules = [
    ["개발", ["개발", "코딩", "프로젝트", "앱", "웹"]],
    ["운동", ["운동", "스포츠", "체력"]],
    ["알고리즘", ["알고리즘", "코테", "문제풀이"]],
    ["동아리", ["동아리", "친목", "스터디"]],
  ] as const;

  return {
    track: matchKeywordRules(normalized, trackRules),
    activity: matchKeywordRules(normalized, activityRules),
  };
}

function matchKeywordRules(
  text: string,
  rules: ReadonlyArray<readonly [string, readonly string[]]>,
): string[] {
  return rules
    .filter(([, keywords]) => keywords.some((keyword) => text.includes(keyword)))
    .map(([label]) => label);
}

function deriveGoal(text: string): string {
  const normalized = text.toLowerCase();
  if (normalized.includes("창업") || normalized.includes("mvp")) {
    return "서비스 MVP 개발";
  }
  if (normalized.includes("취업") || normalized.includes("포트폴리오")) {
    return "취업 포트폴리오 준비";
  }
  if (normalized.includes("ai") || normalized.includes("인공지능")) {
    return "AI 서비스 개발";
  }
  return "AI 서비스 개발";
}

function deriveCodingLevel(text: string): "beginner" | "intermediate" | "advanced" {
  const normalized = text.toLowerCase();
  if (normalized.includes("초급") || normalized.includes("처음") || normalized.includes("기초")) {
    return "beginner";
  }
  if (normalized.includes("고급") || normalized.includes("상급") || normalized.includes("실무")) {
    return "advanced";
  }
  return "intermediate";
}

function deriveLearningPreference(text: string): "lecture" | "project" | "study" | "unknown" {
  if (text.includes("강의") || text.includes("수업")) {
    return "lecture";
  }
  if (text.includes("스터디")) {
    return "study";
  }
  if (text.includes("프로젝트") || text.includes("개발")) {
    return "project";
  }
  return "project";
}

function deriveActivityStyle(text: string): "solo" | "team" | "mixed" | "unknown" {
  if (text.includes("혼자") || text.includes("개인")) {
    return "solo";
  }
  if (text.includes("팀") || text.includes("동아리") || text.includes("친목")) {
    return "team";
  }
  if (text.includes("둘 다") || text.includes("혼합")) {
    return "mixed";
  }
  return "team";
}

function deriveWeeklyHours(text: string): number {
  const match = text.match(/주\s*(\d{1,2})\s*시간/);
  if (!match) {
    return 4;
  }
  return Math.min(Math.max(Number(match[1]), 0), 40);
}

function pageTitle(page: WorkspacePage): string {
  return {
    chat: "AI 트랙을 어떻게 준비할까?",
    roadmap: "학업 로드맵",
    career: "진로/취업",
    project: "프로젝트",
    schedule: "일정",
    logs: "LLM 활용 기록",
    settings: "설정",
  }[page];
}

function pageDescription(page: WorkspacePage): string {
  return {
    chat: "프로필, 메모리, Mini Wiki, 일정 컨텍스트를 함께 보는 상담",
    roadmap: "학기별 과목과 트랙 준비 순서를 정리합니다.",
    career: "진로 고민과 최신 취업 정보를 분리해서 확인합니다.",
    project: "프로젝트와 창업 아이디어를 작은 실행 단위로 정리합니다.",
    schedule: "과제, 시험, 마감일과 D-day를 관리합니다.",
    logs: "LLM 사용 목적과 검토 내용을 제출용으로 정리합니다.",
    settings: "프로필, 메모리, 외부 연동 상태를 관리합니다.",
  }[page];
}

function placeholderCards(page: WorkspacePage) {
  const common = {
    roadmap: [
      ["학기별 로드맵", "1학년부터 4학년까지 과목과 프로젝트 흐름을 보여줍니다."],
      ["트랙 비교", "AI, 웹, 보안, IoT 등 관심 분야별 준비 과정을 비교합니다."],
      ["다음 행동", "현재 학년 기준으로 이번 주에 할 일을 추천합니다."],
    ],
    career: [
      ["관심 직무", "백엔드, AI, 데이터 등 직무별 준비 항목을 정리합니다."],
      ["최신 정보", "추후 Google grounding으로 공고와 공모전 정보를 보강합니다."],
      ["포트폴리오", "프로젝트 경험과 기록할 산출물을 연결합니다."],
    ],
    project: [
      ["아이디어", "문제 정의와 대상 사용자를 먼저 기록합니다."],
      ["실행 단위", "1주 안에 만들 수 있는 작은 데모로 쪼갭니다."],
      ["근거", "전공 로드맵과 진로 목표에 맞는 프로젝트인지 확인합니다."],
    ],
    schedule: [
      ["자연어 입력", "과제 문장을 제목, 과목, 마감일로 추출합니다."],
      ["D-day", "다가오는 과제와 시험을 우선순위로 보여줍니다."],
      ["Calendar", "저장된 일정을 Google Calendar event payload로 내보냅니다."],
    ],
  } as const;

  return (common[page as keyof typeof common] ?? common.roadmap).map(([title, description]) => ({
    title,
    description,
  }));
}

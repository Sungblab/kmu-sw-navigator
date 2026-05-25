import {
  BriefcaseBusiness,
  CalendarDays,
  MessageSquareText,
  PanelLeftClose,
  PanelLeftOpen,
  Plus,
  Settings,
  Trash2,
  X,
} from "lucide-react";
import type { PointerEvent as ReactPointerEvent } from "react";

import type { ChatSessionSummary } from "../types/api";
import type { WorkspacePage } from "../types/navigator";

const workspaceItems: Array<{
  id: WorkspacePage;
  label: string;
  icon: typeof MessageSquareText;
}> = [
  { id: "chat", label: "AI 상담", icon: MessageSquareText },
  { id: "career", label: "추천 보드", icon: BriefcaseBusiness },
  { id: "schedule", label: "일정", icon: CalendarDays },
];

interface NavigationProps {
  activePage: WorkspacePage;
  activeSessionId: string | null;
  isCollapsed?: boolean;
  sessions: ChatSessionSummary[];
  setActivePage: (page: WorkspacePage) => void;
  onNewChat: () => void;
  onOpenSession: (sessionId: string) => void;
  onDeleteSession: (sessionId: string) => void;
  onToggleCollapse?: () => void;
  onResizeStart?: (event: ReactPointerEvent<HTMLDivElement>) => void;
}

interface MobileDrawerProps extends NavigationProps {
  isOpen: boolean;
  onClose: () => void;
}

export function Sidebar(props: NavigationProps) {
  const {
    activePage,
    activeSessionId,
    isCollapsed = false,
    sessions,
    setActivePage,
    onNewChat,
    onOpenSession,
    onDeleteSession,
    onToggleCollapse,
    onResizeStart,
  } = props;

  if (isCollapsed) {
    return (
      <aside className="relative hidden h-full min-h-0 min-w-0 overflow-hidden border-r border-[#ded7cb] bg-[#f1ede5] p-2 lg:flex lg:flex-col lg:items-center">
        <button
          className="grid h-9 w-9 place-items-center rounded-lg border border-[#c9c0b3] bg-[#fffdf8] text-sm font-bold"
          type="button"
          aria-label="왼쪽 사이드바 펼치기"
          title="사이드바 펼치기"
          onClick={onToggleCollapse}
        >
          <PanelLeftOpen className="h-4 w-4" aria-hidden="true" />
        </button>
        <button
          className="mt-3 grid h-9 w-9 place-items-center rounded-lg bg-[#191817] text-[#fffdf8]"
          type="button"
          aria-label="새 상담"
          title="새 상담"
          onClick={onNewChat}
        >
          <Plus className="h-4 w-4" aria-hidden="true" />
        </button>
        <div className="mt-4 flex w-full flex-col items-center gap-1">
          {workspaceItems.map((item) => {
            const Icon = item.icon;
            const selected = activePage === item.id;
            return (
              <button
                className={`grid h-9 w-9 place-items-center rounded-lg ${
                  selected
                    ? "border border-[#ded7cb] bg-[#fffdf8] text-[#191817]"
                    : "text-[#3d3b37] hover:bg-[#f7f2ea]"
                }`}
                key={item.id}
                type="button"
                aria-label={item.label}
                title={item.label}
                onClick={() => setActivePage(item.id)}
              >
                <Icon className="h-4 w-4" aria-hidden="true" />
              </button>
            );
          })}
        </div>
        <button
          className="mt-auto grid h-9 w-9 place-items-center rounded-lg text-[#3d3b37] hover:bg-[#f7f2ea]"
          type="button"
          aria-label="설정"
          title="설정"
          onClick={() => setActivePage("settings")}
        >
          <Settings className="h-4 w-4" aria-hidden="true" />
        </button>
      </aside>
    );
  }

  return (
    <aside className="relative hidden h-full min-h-0 min-w-0 overflow-hidden border-r border-[#ded7cb] bg-[#f1ede5] p-3 lg:block">
      {onResizeStart ? (
        <div
          className="absolute right-[-3px] top-0 z-10 hidden h-full w-2 cursor-col-resize lg:block"
          role="separator"
          aria-label="왼쪽 사이드바 폭 조절"
          aria-orientation="vertical"
          onPointerDown={onResizeStart}
        />
      ) : null}
      <div className="flex items-start justify-between gap-2">
        <BrandHeader />
        <button
          className="grid h-8 w-8 shrink-0 place-items-center rounded-lg border border-[#c9c0b3] bg-[#fffdf8] text-[#3d3b37]"
          type="button"
          aria-label="왼쪽 사이드바 접기"
          title="사이드바 접기"
          onClick={onToggleCollapse}
        >
          <PanelLeftClose className="h-4 w-4" aria-hidden="true" />
        </button>
      </div>

      <button
        className="h-10 w-full rounded-lg bg-[#191817] text-sm font-semibold text-[#fffdf8]"
        type="button"
        onClick={onNewChat}
      >
        새 상담
      </button>

      <SidebarLabel>메뉴</SidebarLabel>
      <WorkspaceNav activePage={activePage} setActivePage={setActivePage} />

      <SidebarLabel>최근 상담</SidebarLabel>
      <RecentChats
        activeSessionId={activeSessionId}
        sessions={sessions}
        setActivePage={setActivePage}
        onOpenSession={onOpenSession}
        onDeleteSession={onDeleteSession}
      />

      <div className="absolute bottom-3 left-3 right-3 hidden space-y-1 lg:block">
        <UtilityNav setActivePage={setActivePage} itemHeight="h-9" />
      </div>
    </aside>
  );
}

export function MobileDrawer({
  activePage,
  activeSessionId,
  isOpen,
  sessions,
  setActivePage,
  onClose,
  onNewChat,
  onOpenSession,
  onDeleteSession,
}: MobileDrawerProps) {
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
          <BrandHeader compact />
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
          <SidebarLabel>메뉴</SidebarLabel>
          <WorkspaceNav activePage={activePage} setActivePage={setActivePage} mobile />

          <SidebarLabel>최근 상담</SidebarLabel>
          <RecentChats
            activeSessionId={activeSessionId}
            sessions={sessions}
            setActivePage={setActivePage}
            onOpenSession={onOpenSession}
            onDeleteSession={onDeleteSession}
          />
        </div>

        <div className="border-t border-[#ded7cb] pt-2">
          <UtilityNav setActivePage={setActivePage} itemHeight="h-10" />
        </div>
      </aside>
    </div>
  );
}

function BrandHeader({ compact = false }: { compact?: boolean }) {
  return (
    <div className={`flex min-w-0 items-center gap-3 ${compact ? "" : "px-2 pb-4 pt-1"}`}>
      <div className="grid h-8 w-8 shrink-0 place-items-center rounded-lg border border-[#c9c0b3] bg-[#fffdf8] text-sm font-bold">
        K
      </div>
      <div className="min-w-0">
        <strong className="block truncate text-sm font-semibold tracking-normal">
          SW Navigator
        </strong>
        <span className="block truncate text-xs text-[#716c63]">내 학업 내비게이터</span>
      </div>
    </div>
  );
}

function WorkspaceNav({
  activePage,
  setActivePage,
  mobile = false,
}: {
  activePage: WorkspacePage;
  setActivePage: (page: WorkspacePage) => void;
  mobile?: boolean;
}) {
  return (
    <div className="space-y-1">
      {workspaceItems.map((item) => {
        const Icon = item.icon;
        const selected = activePage === item.id;
        return (
          <button
            className={`flex ${mobile ? "min-h-10" : "min-h-9"} w-full items-center justify-between rounded-lg px-2.5 text-sm ${
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
          </button>
        );
      })}
    </div>
  );
}

function RecentChats({
  activeSessionId,
  sessions,
  setActivePage,
  onOpenSession,
  onDeleteSession,
}: {
  activeSessionId: string | null;
  sessions: ChatSessionSummary[];
  setActivePage: (page: WorkspacePage) => void;
  onOpenSession: (sessionId: string) => void;
  onDeleteSession: (sessionId: string) => void;
}) {
  if (!sessions.length) {
    return (
      <div className="rounded-lg border border-[#ded7cb] bg-[#fffdf8] px-2.5 py-2 text-xs leading-5 text-[#716c63]">
        새 상담을 시작하면 최근 기록이 여기에 표시됩니다.
      </div>
    );
  }

  return (
    <div className="space-y-1">
      {sessions.map((chat) => {
        const selected = chat.id === activeSessionId;
        return (
          <div
            className={`group flex items-start gap-1 rounded-lg px-2 py-2 ${
              selected
                ? "border border-[#ded7cb] bg-[#fffdf8]"
                : "text-[#3d3b37] hover:bg-[#f7f2ea]"
            }`}
            key={chat.id}
          >
            <button
              className="min-w-0 flex-1 text-left"
              type="button"
              onClick={() => (sessions.length ? onOpenSession(chat.id) : setActivePage("chat"))}
            >
              <span className="flex items-center justify-between gap-2">
                <strong className="min-w-0 truncate text-sm font-semibold">{chat.title ?? "새 상담"}</strong>
                {chat.updated_at ? (
                  <span className="shrink-0 text-[11px] text-[#938d83]">
                    {formatSessionDate(chat.updated_at)}
                  </span>
                ) : null}
              </span>
              <span className="mt-1 line-clamp-2 text-xs leading-5 text-[#716c63]">
                {chat.last_message_preview ?? chatIntentLabel(chat.intent)}
              </span>
            </button>
            <button
              className="grid h-7 w-7 shrink-0 place-items-center rounded-md text-[#938d83] opacity-70 hover:bg-[#eadfd1] hover:text-[#9b3f24] group-hover:opacity-100"
              type="button"
              aria-label={`${chat.title ?? "상담"} 삭제`}
              title="상담 기록 삭제"
              onClick={(event) => {
                event.stopPropagation();
                onDeleteSession(chat.id);
              }}
            >
              <Trash2 className="h-3.5 w-3.5" aria-hidden="true" />
            </button>
          </div>
        );
      })}
    </div>
  );
}

function formatSessionDate(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "";
  }
  return date.toLocaleDateString("ko-KR", { month: "numeric", day: "numeric" });
}

function chatIntentLabel(intent: string | null): string {
  const labels: Record<string, string> = {
    academic_advisor: "학업 상담",
    career_advisor: "진로 상담",
    startup_project_mentor: "창업/프로젝트",
    schedule_assistant: "일정 정리",
    general: "일반 상담",
  };
  return intent ? labels[intent] ?? "일반 상담" : "일반 상담";
}

function UtilityNav({
  setActivePage,
  itemHeight,
}: {
  setActivePage: (page: WorkspacePage) => void;
  itemHeight: "h-9" | "h-10";
}) {
  return (
    <button
      className={`flex ${itemHeight} w-full items-center gap-2 rounded-lg px-2.5 text-sm text-[#3d3b37] hover:bg-[#f7f2ea]`}
      type="button"
      onClick={() => setActivePage("settings")}
    >
      <Settings className="h-4 w-4" aria-hidden="true" />
      설정
    </button>
  );
}

function SidebarLabel({ children }: { children: string }) {
  return (
    <p className="mb-2 ml-2 mt-5 text-[11px] font-bold uppercase tracking-[0.06em] text-[#938d83]">
      {children}
    </p>
  );
}

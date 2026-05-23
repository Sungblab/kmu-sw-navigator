import { Menu, PanelRight, RefreshCw } from "lucide-react";

import { pageDescription, pageTitle } from "../lib/navigator";
import type { AuthSessionSummary } from "../lib/supabase";
import type { WorkspacePage } from "../types/navigator";

export function TopBar({
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
          {authSession ? "Supabase session" : "로그인 필요"}
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

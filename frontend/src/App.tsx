import { BookOpen, CalendarDays, ClipboardList, MessageSquareText } from "lucide-react";

const features = [
  {
    title: "RAG 챗봇",
    description: "국민대/소프트웨어학부 자료를 검색하고 출처 기반 답변을 제공합니다.",
    icon: MessageSquareText,
  },
  {
    title: "트랙/활동 추천",
    description: "관심 분야와 목표를 입력하면 조건 기반 추천 결과를 보여줍니다.",
    icon: BookOpen,
  },
  {
    title: "일정 D-day",
    description: "자연어 일정 입력을 구조화하고 마감까지 남은 기간을 계산합니다.",
    icon: CalendarDays,
  },
  {
    title: "LLM 활용 기록",
    description: "Gemini API와 Codex 개발 활용 과정을 제출용 기록으로 남깁니다.",
    icon: ClipboardList,
  },
];

export default function App() {
  return (
    <main className="min-h-screen bg-slate-950 text-slate-50">
      <section className="mx-auto flex min-h-screen w-full max-w-6xl flex-col px-6 py-10">
        <header className="flex flex-col gap-3 border-b border-slate-800 pb-8">
          <p className="text-sm font-medium text-sky-300">국민대학교 소프트웨어융합대학</p>
          <h1 className="text-4xl font-bold tracking-normal">kmu-sw-navigator</h1>
          <p className="max-w-3xl text-base leading-7 text-slate-300">
            국민대학교 소프트웨어융합대학 학생이 커리큘럼, 트랙, 진로, 프로젝트, 일정을
            한 곳에서 탐색할 수 있도록 돕는 개인화 RAG 기반 AI 내비게이터입니다.
          </p>
        </header>

        <div className="grid flex-1 gap-4 py-8 md:grid-cols-2">
          {features.map((feature) => {
            const Icon = feature.icon;
            return (
              <article
                key={feature.title}
                className="rounded-lg border border-slate-800 bg-slate-900 p-5"
              >
                <Icon className="mb-4 h-6 w-6 text-sky-300" aria-hidden="true" />
                <h2 className="text-xl font-semibold">{feature.title}</h2>
                <p className="mt-2 text-sm leading-6 text-slate-300">{feature.description}</p>
              </article>
            );
          })}
        </div>
      </section>
    </main>
  );
}

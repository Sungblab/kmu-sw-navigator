import type { Memory } from "../types/api";
import type {
  RecommendationInputContext,
  RecommendationInputDraft,
  WorkspacePage,
} from "../types/navigator";

export function buildRecommendationInputContext(memories: Memory[]): RecommendationInputContext {
  const memoryText = memories
    .map((memory) => `${memory.natural_text} ${Object.values(memory.value_json).join(" ")}`)
    .join(" ");
  const interests = deriveInterestKeywords(memoryText);

  return {
    trackInterests: interests.track,
    activityInterests: interests.activity,
    goal: deriveGoal(memoryText),
    codingLevel: deriveCodingLevel(memoryText),
    preference: deriveLearningPreference(memoryText),
    activityStyle: deriveActivityStyle(memoryText),
    weeklyHours: deriveWeeklyHours(memoryText),
    sourceLabel: memories.length ? "내 관심 정보" : "대화에서 파악한 정보 없음",
  };
}

export function recommendationContextToDraft(
  context: RecommendationInputContext,
): RecommendationInputDraft {
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

export function recommendationDraftToContext(
  draft: RecommendationInputDraft,
  sourceLabel: string,
): RecommendationInputContext {
  return {
    trackInterests: splitRecommendationTerms(draft.trackInterestsText),
    activityInterests: splitRecommendationTerms(draft.activityInterestsText),
    goal: draft.goal.trim(),
    codingLevel: draft.codingLevel,
    preference: draft.preference,
    activityStyle: draft.activityStyle,
    weeklyHours: Math.min(Math.max(Number(draft.weeklyHours) || 0, 0), 40),
    sourceLabel,
  };
}

export function pageTitle(page: WorkspacePage): string {
  return {
    chat: "AI 트랙을 어떻게 준비할까?",
    roadmap: "학업 로드맵",
    career: "진로/취업",
    project: "프로젝트",
    schedule: "일정",
    settings: "설정",
  }[page];
}

export function pageDescription(page: WorkspacePage): string {
  return {
    chat: "내 관심사와 학업 정보를 바탕으로 상담합니다.",
    roadmap: "학기별 과목과 트랙 준비 순서를 정리합니다.",
    career: "진로 고민과 최신 취업 정보를 분리해서 확인합니다.",
    project: "프로젝트와 창업 아이디어를 작은 실행 단위로 정리합니다.",
    schedule: "과제, 시험, 마감일과 D-day를 관리합니다.",
    settings: "계정과 기본 학업 정보를 관리합니다.",
  }[page];
}

export function placeholderCards(page: WorkspacePage) {
  const common = {
    roadmap: [
      ["학기별 로드맵", "1학년부터 4학년까지 과목과 프로젝트 흐름을 보여줍니다."],
      ["트랙 비교", "AI, 웹, 보안, IoT 등 관심 분야별 준비 과정을 비교합니다."],
      ["다음 행동", "현재 학년 기준으로 이번 주에 할 일을 추천합니다."],
    ],
    career: [
      ["관심 직무", "백엔드, AI, 데이터 등 직무별 준비 항목을 정리합니다."],
      ["최신 정보", "진로와 공모전 정보를 함께 확인합니다."],
      ["포트폴리오", "프로젝트 경험과 기록할 산출물을 연결합니다."],
    ],
    project: [
      ["아이디어", "문제 정의와 대상 사용자를 먼저 기록합니다."],
      ["실행 단위", "1주 안에 끝낼 수 있는 작은 작업으로 쪼갭니다."],
      ["근거", "전공 로드맵과 진로 목표에 맞는 프로젝트인지 확인합니다."],
    ],
    schedule: [
      ["자연어 입력", "과제 문장을 제목, 과목, 마감일로 추출합니다."],
      ["D-day", "다가오는 과제와 시험을 우선순위로 보여줍니다."],
      ["완료 관리", "끝낸 일정은 완료 처리하고 목록에서 정리합니다."],
    ],
  } as const;

  return (common[page as keyof typeof common] ?? common.roadmap).map(([title, description]) => ({
    title,
    description,
  }));
}

function splitRecommendationTerms(value: string): string[] {
  const terms = value
    .split(/[,\n]/)
    .map((term) => term.trim())
    .filter(Boolean);

  return Array.from(new Set(terms)).slice(0, 8);
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
  return "";
}

function deriveCodingLevel(text: string): "beginner" | "intermediate" | "advanced" | "unknown" {
  const normalized = text.toLowerCase();
  if (normalized.includes("초급") || normalized.includes("처음") || normalized.includes("기초")) {
    return "beginner";
  }
  if (normalized.includes("고급") || normalized.includes("상급") || normalized.includes("실무")) {
    return "advanced";
  }
  return "unknown";
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
  return "unknown";
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
  return "unknown";
}

function deriveWeeklyHours(text: string): number {
  const match = text.match(/주\s*(\d{1,2})\s*시간/);
  if (!match) {
    return 0;
  }
  return Math.min(Math.max(Number(match[1]), 0), 40);
}

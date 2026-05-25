import type { ChatResponse } from "./api";

export type WorkspacePage =
  | "chat"
  | "roadmap"
  | "career"
  | "project"
  | "schedule"
  | "logs"
  | "settings";

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  text: string;
  response?: ChatResponse;
  isPending?: boolean;
}

export interface RecommendationInputContext {
  trackInterests: string[];
  activityInterests: string[];
  goal: string;
  codingLevel: "beginner" | "intermediate" | "advanced";
  preference: "lecture" | "project" | "study" | "unknown";
  activityStyle: "solo" | "team" | "mixed" | "unknown";
  weeklyHours: number;
  sourceLabel: string;
}

export interface RecommendationInputDraft {
  trackInterestsText: string;
  activityInterestsText: string;
  goal: string;
  codingLevel: RecommendationInputContext["codingLevel"];
  preference: RecommendationInputContext["preference"];
  activityStyle: RecommendationInputContext["activityStyle"];
  weeklyHours: number;
}

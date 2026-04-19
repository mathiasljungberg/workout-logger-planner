import { useQuery } from "@tanstack/react-query";

import { api } from "./client";
import type {
  AnalyticsSummary,
  AuthUser,
  Exercise,
  PlannedWorkout,
  TrainingBlock,
  WorkoutSession,
  WorkoutTemplate,
} from "./types";

export const queryKeys = {
  me: ["me"] as const,
  exercises: (includeArchived = false) => ["exercises", { includeArchived }] as const,
  templates: ["templates"] as const,
  blocks: ["blocks"] as const,
  block: (id: string) => ["blocks", id] as const,
  plannedWorkouts: (range?: { start?: string; end?: string }) =>
    ["planned-workouts", range ?? {}] as const,
  session: (id: string) => ["sessions", id] as const,
  sessions: ["sessions"] as const,
  analyticsSummary: ["analytics", "summary"] as const,
};

export function useMe() {
  return useQuery({
    queryKey: queryKeys.me,
    queryFn: () => api.get<AuthUser>("/auth/me"),
    retry: false,
    staleTime: 60_000,
  });
}

export function useExercises(includeArchived = false) {
  return useQuery({
    queryKey: queryKeys.exercises(includeArchived),
    queryFn: () =>
      api.get<Exercise[]>(
        includeArchived ? "/exercises?include_archived=true" : "/exercises",
      ),
  });
}

export function useTemplates() {
  return useQuery({
    queryKey: queryKeys.templates,
    queryFn: () => api.get<WorkoutTemplate[]>("/templates"),
  });
}

export function useBlocks() {
  return useQuery({
    queryKey: queryKeys.blocks,
    queryFn: () => api.get<TrainingBlock[]>("/blocks"),
  });
}

export function usePlannedWorkouts(range?: { start?: string; end?: string }) {
  const query = new URLSearchParams();
  if (range?.start) query.set("start", range.start);
  if (range?.end) query.set("end", range.end);
  const suffix = query.toString();
  return useQuery({
    queryKey: queryKeys.plannedWorkouts(range),
    queryFn: () =>
      api.get<PlannedWorkout[]>(suffix ? `/planned-workouts?${suffix}` : "/planned-workouts"),
  });
}

export function useSession(sessionId: string | undefined) {
  return useQuery({
    queryKey: queryKeys.session(sessionId ?? ""),
    queryFn: () => api.get<WorkoutSession>(`/sessions/${sessionId}`),
    enabled: Boolean(sessionId),
  });
}

export function useAnalyticsSummary() {
  return useQuery({
    queryKey: queryKeys.analyticsSummary,
    queryFn: () => api.get<AnalyticsSummary>("/analytics/summary"),
  });
}

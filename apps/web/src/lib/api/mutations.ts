import { useMutation, useQueryClient } from "@tanstack/react-query";

import { api } from "./client";
import { queryKeys } from "./queries";
import type {
  GeneratedPlannedWorkout,
  GeneratePlannedWorkoutsPayload,
  PlannedWorkout,
  PlannedWorkoutCreate,
  TrainingBlock,
  TrainingBlockCreate,
  WorkoutSession,
  WorkoutSessionCreate,
  WorkoutTemplate,
  WorkoutTemplateCreate,
} from "./types";

export function useCreateBlock() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: TrainingBlockCreate) => api.post<TrainingBlock>("/blocks", payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.blocks });
    },
  });
}

export function useUpdateBlock() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: TrainingBlockCreate }) =>
      api.patch<TrainingBlock>(`/blocks/${id}`, payload),
    onSuccess: (_data, variables) => {
      qc.invalidateQueries({ queryKey: queryKeys.blocks });
      qc.invalidateQueries({ queryKey: queryKeys.block(variables.id) });
    },
  });
}

export function usePropagateBlockProgressions() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (blockId: string) =>
      api.post<TrainingBlock>(`/blocks/${blockId}/propagate-progressions`),
    onSuccess: (_data, blockId) => {
      qc.invalidateQueries({ queryKey: queryKeys.blocks });
      qc.invalidateQueries({ queryKey: queryKeys.block(blockId) });
    },
  });
}

export function useGeneratePlannedWorkouts() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ blockId, payload }: { blockId: string; payload: GeneratePlannedWorkoutsPayload }) =>
      api.post<GeneratedPlannedWorkout[]>(`/blocks/${blockId}/generate-planned-workouts`, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["planned-workouts"] });
    },
  });
}

export function useCreateTemplate() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: WorkoutTemplateCreate) =>
      api.post<WorkoutTemplate>("/templates", payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.templates });
    },
  });
}

export function useUpdateTemplate() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: WorkoutTemplateCreate }) =>
      api.patch<WorkoutTemplate>(`/templates/${id}`, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.templates });
    },
  });
}

export function useCreatePlannedWorkout() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: PlannedWorkoutCreate) =>
      api.post<PlannedWorkout>("/planned-workouts", payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["planned-workouts"] });
    },
  });
}

export function useUpdatePlannedWorkout() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: PlannedWorkoutCreate }) =>
      api.patch<PlannedWorkout>(`/planned-workouts/${id}`, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["planned-workouts"] });
    },
  });
}

export function useCreateSession() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: WorkoutSessionCreate) =>
      api.post<WorkoutSession>("/sessions", payload),
    onSuccess: (session) => {
      qc.invalidateQueries({ queryKey: queryKeys.sessions });
      qc.invalidateQueries({ queryKey: ["planned-workouts"] });
      qc.setQueryData(queryKeys.session(session.id), session);
    },
  });
}

export function useUpdateSession() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: WorkoutSessionCreate }) =>
      api.patch<WorkoutSession>(`/sessions/${id}`, payload),
    onSuccess: (session) => {
      qc.invalidateQueries({ queryKey: queryKeys.sessions });
      qc.invalidateQueries({ queryKey: ["planned-workouts"] });
      qc.invalidateQueries({ queryKey: queryKeys.analyticsSummary });
      qc.setQueryData(queryKeys.session(session.id), session);
    },
  });
}

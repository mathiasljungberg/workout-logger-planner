import type { components } from "./generated";

type S = components["schemas"];

export type AuthUser = S["AuthUser"];
export type Exercise = S["ExerciseRead"];
export type ExerciseCreate = S["ExerciseCreate"];
export type WorkoutTemplate = S["WorkoutTemplateRead"];
export type WorkoutTemplateCreate = S["WorkoutTemplateCreate"];
export type TrainingBlock = S["TrainingBlockDetail"];
export type TrainingBlockCreate = S["TrainingBlockCreate"];
export type BlockWorkout = S["BlockWorkoutRead"];
export type BlockWorkoutExercise = S["BlockWorkoutExerciseRead"];
export type ProgressionRule = S["ProgressionRuleRead"];
export type PlannedWorkout = S["PlannedWorkoutDetail"];
export type PlannedWorkoutExercise = S["PlannedWorkoutExerciseRead"];
export type PlannedWorkoutCreate = S["PlannedWorkoutCreate"];
export type GeneratedPlannedWorkout = S["GeneratedPlannedWorkoutRead"];
export type GeneratePlannedWorkoutsPayload = S["GeneratePlannedWorkoutsPayload"];
export type WorkoutSession = S["WorkoutSessionDetail"];
export type WorkoutSessionExercise = S["WorkoutSessionExerciseRead"];
export type WorkoutSessionCreate = S["WorkoutSessionCreate"];
export type SetEntry = S["SetEntryRead"];
export type SetEntryPayload = S["SetEntryPayload"];
export type AnalyticsSummary = S["AnalyticsResponse"];

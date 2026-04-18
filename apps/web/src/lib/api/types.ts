export type Exercise = {
  id: string;
  name: string;
  modality: string;
  default_measure_type: string;
  notes?: string | null;
};

export type TemplateExercise = {
  id: string;
  exercise_id: string;
  exercise_name: string;
  order_index: number;
  notes?: string | null;
  target_sets?: number | null;
  target_reps?: string | null;
  target_weight?: number | null;
};

export type WorkoutTemplate = {
  id: string;
  name: string;
  description?: string | null;
  exercises: TemplateExercise[];
};

export type BlockExercise = TemplateExercise & {
  progression_rule_id?: string | null;
};

export type BlockWorkout = {
  id: string;
  name: string;
  week_index: number;
  day_index: number;
  notes?: string | null;
  exercises: BlockExercise[];
};

export type ProgressionRule = {
  id: string;
  name: string;
  rule_type: string;
  config_json?: Record<string, unknown> | null;
  deload_strategy?: string | null;
  notes?: string | null;
};

export type TrainingBlock = {
  id: string;
  name: string;
  goal?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  status: string;
  progression_rules: ProgressionRule[];
  workouts: BlockWorkout[];
};

export type PlannedWorkoutExercise = {
  id: string;
  exercise_id: string;
  exercise_name_snapshot: string;
  order_index: number;
  target_sets?: number | null;
  target_reps?: string | null;
  target_weight?: number | null;
  notes?: string | null;
};

export type PlannedWorkout = {
  id: string;
  planned_date: string;
  status: string;
  title: string;
  notes?: string | null;
  session_id?: string | null;
  exercises: PlannedWorkoutExercise[];
};

export type SetEntry = {
  id?: string;
  set_number: number;
  completed: boolean;
  reps?: number | null;
  weight?: number | null;
  comment?: string | null;
};

export type WorkoutSessionExercise = {
  id: string;
  exercise_name_snapshot: string;
  completed: boolean;
  set_entries: SetEntry[];
};

export type WorkoutSession = {
  id: string;
  planned_workout_id?: string | null;
  started_at: string;
  ended_at?: string | null;
  status: string;
  title: string;
  session_notes?: string | null;
  exercises: WorkoutSessionExercise[];
};

export type AnalyticsSummary = {
  adherence_rate: number;
  planned_count: number;
  completed_planned_count: number;
  total_sessions: number;
  total_completed_sets: number;
  total_volume: number;
  recent_volume: Array<{ date: string; volume: number }>;
};


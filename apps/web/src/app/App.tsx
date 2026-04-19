import { Navigate, Route, Routes, useNavigate } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";

import { AppShell } from "../components/AppShell";
import { useMe } from "../lib/api/queries";
import { useCreateSession } from "../lib/api/mutations";
import { queryKeys } from "../lib/api/queries";
import { PlannedWorkout } from "../lib/api/types";
import { AnalyticsPage } from "../features/analytics/AnalyticsPage";
import { LoginPage } from "../features/auth/LoginPage";
import { BlocksPage } from "../features/blocks/BlocksPage";
import { CalendarPage } from "../features/calendar/CalendarPage";
import { SessionPage } from "../features/session/SessionPage";
import { SettingsPage } from "../features/settings/SettingsPage";
import { TemplatesPage } from "../features/templates/TemplatesPage";

function ProtectedApp({ onStartSession }: { onStartSession: (plannedWorkout: PlannedWorkout) => Promise<void> }) {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route path="/calendar" element={<CalendarPage onStartSession={onStartSession} />} />
        <Route path="/templates" element={<TemplatesPage />} />
        <Route path="/blocks" element={<BlocksPage />} />
        <Route path="/session/:sessionId" element={<SessionPage />} />
        <Route path="/analytics" element={<AnalyticsPage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/calendar" replace />} />
    </Routes>
  );
}

export function App() {
  const { data: user, isLoading } = useMe();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const createSession = useCreateSession();

  async function onStartSession(plannedWorkout: PlannedWorkout) {
    if (plannedWorkout.session_id) {
      navigate(`/session/${plannedWorkout.session_id}`);
      return;
    }
    const session = await createSession.mutateAsync({
      planned_workout_id: plannedWorkout.id,
      started_at: new Date().toISOString(),
      status: "in_progress",
      title: plannedWorkout.title,
      session_notes: plannedWorkout.notes,
      exercises: plannedWorkout.exercises.map((exercise) => ({
        planned_workout_exercise_id: exercise.id,
        exercise_id: exercise.exercise_id,
        order_index: exercise.order_index,
        exercise_name_snapshot: exercise.exercise_name_snapshot,
        target_sets: exercise.target_sets,
        target_reps: exercise.target_reps,
        target_weight: exercise.target_weight,
        notes: exercise.notes,
        completed: false,
        set_entries: Array.from({ length: exercise.target_sets ?? 1 }, (_, index) => ({
          set_number: index + 1,
          set_type: "working",
          completed: false,
        })),
      })),
    });
    navigate(`/session/${session.id}`);
  }

  async function refreshAuth() {
    await queryClient.invalidateQueries({ queryKey: queryKeys.me });
  }

  if (isLoading) {
    return <div className="login">Loading...</div>;
  }

  return user ? (
    <ProtectedApp onStartSession={onStartSession} />
  ) : (
    <Routes>
      <Route path="/login" element={<LoginPage authenticated={false} onLogin={refreshAuth} />} />
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}

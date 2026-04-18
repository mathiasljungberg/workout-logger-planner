import { useEffect, useState } from "react";
import { Navigate, Route, Routes, useNavigate } from "react-router-dom";

import { AppShell } from "../components/AppShell";
import { api } from "../lib/api/client";
import { PlannedWorkout } from "../lib/api/types";
import { AnalyticsPage } from "../features/analytics/AnalyticsPage";
import { LoginPage } from "../features/auth/LoginPage";
import { BlocksPage } from "../features/blocks/BlocksPage";
import { CalendarPage } from "../features/calendar/CalendarPage";
import { SessionPage } from "../features/session/SessionPage";
import { SettingsPage } from "../features/settings/SettingsPage";
import { TemplatesPage } from "../features/templates/TemplatesPage";

type AuthUser = { id: string; username: string };

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
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  async function refreshAuth() {
    try {
      const currentUser = await api.get<AuthUser>("/auth/me");
      setUser(currentUser);
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refreshAuth().catch(console.error);
  }, []);

  async function onStartSession(plannedWorkout: PlannedWorkout) {
    if (plannedWorkout.session_id) {
      navigate(`/session/${plannedWorkout.session_id}`);
      return;
    }
    const session = await api.post<{ id: string }>("/sessions", {
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
        set_entries: Array.from({ length: exercise.target_sets ?? 1 }, (_, index) => ({
          set_number: index + 1,
          completed: false,
        })),
      })),
    });
    navigate(`/session/${session.id}`);
  }

  if (loading) {
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


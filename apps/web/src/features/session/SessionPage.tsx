import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import { Card } from "../../components/Card";
import { Page } from "../../components/Page";
import { api } from "../../lib/api/client";
import { WorkoutSession } from "../../lib/api/types";

export function SessionPage() {
  const { sessionId = "" } = useParams();
  const [session, setSession] = useState<WorkoutSession | null>(null);

  useEffect(() => {
    api.get<WorkoutSession>(`/sessions/${sessionId}`).then(setSession).catch(console.error);
  }, [sessionId]);

  if (!session) {
    return <Page title="Session">Loading session...</Page>;
  }

  return (
    <Page title={session.title} description="Track sets, completion, and comments during the workout.">
      <div className="grid">
        {session.exercises.map((exercise) => (
          <Card key={exercise.id}>
            <div className="row">
              <h3>{exercise.exercise_name_snapshot}</h3>
              <span className={`pill ${exercise.completed ? "pill--completed" : ""}`}>
                {exercise.completed ? "done" : "active"}
              </span>
            </div>
            <ul className="list">
              {exercise.set_entries.map((setEntry) => (
                <li key={setEntry.id ?? setEntry.set_number}>
                  Set {setEntry.set_number}: {setEntry.reps ?? "-"} reps @ {setEntry.weight ?? "-"} kg
                </li>
              ))}
            </ul>
          </Card>
        ))}
      </div>
    </Page>
  );
}


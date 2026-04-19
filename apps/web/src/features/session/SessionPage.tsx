import { useParams } from "react-router-dom";

import { Card } from "../../components/Card";
import { Page } from "../../components/Page";
import { QueryBoundary } from "../../components/QueryBoundary";
import { useSession } from "../../lib/api/queries";

export function SessionPage() {
  const { sessionId = "" } = useParams();
  const { data: session, isLoading, error } = useSession(sessionId);

  return (
    <Page
      title={session?.title ?? "Session"}
      description="Track sets, completion, and comments during the workout."
    >
      <QueryBoundary isLoading={isLoading} error={error} loadingLabel="Loading session...">
        {session ? (
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
        ) : null}
      </QueryBoundary>
    </Page>
  );
}

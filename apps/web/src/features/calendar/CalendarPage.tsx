import { Card } from "../../components/Card";
import { Page } from "../../components/Page";
import { QueryBoundary } from "../../components/QueryBoundary";
import { usePlannedWorkouts } from "../../lib/api/queries";
import { PlannedWorkout } from "../../lib/api/types";

type CalendarPageProps = {
  onStartSession: (plannedWorkout: PlannedWorkout) => Promise<void>;
};

export function CalendarPage({ onStartSession }: CalendarPageProps) {
  const { data: items = [], isLoading, error } = usePlannedWorkouts();

  return (
    <Page
      title="Calendar"
      description="Planned workouts are expanded into explicit calendar items so changes to blocks do not rewrite history."
    >
      <QueryBoundary isLoading={isLoading} error={error} loadingLabel="Loading calendar...">
        <div className="grid">
          {items.map((item) => (
            <Card key={item.id}>
              <div className="row">
                <div>
                  <h3>{item.title}</h3>
                  <p>{item.planned_date}</p>
                </div>
                <span className={`pill pill--${item.status}`}>{item.status}</span>
              </div>
              <ul className="list">
                {item.exercises.map((exercise) => (
                  <li key={exercise.id}>
                    {exercise.exercise_name_snapshot}
                    {exercise.target_sets ? ` • ${exercise.target_sets} sets` : ""}
                    {exercise.target_reps ? ` • ${exercise.target_reps} reps` : ""}
                  </li>
                ))}
              </ul>
              <button onClick={() => onStartSession(item)}>
                {item.session_id ? "View session" : "Start session"}
              </button>
            </Card>
          ))}
          {items.length === 0 ? (
            <Card>No planned workouts yet. Create a block or add one via the API.</Card>
          ) : null}
        </div>
      </QueryBoundary>
    </Page>
  );
}

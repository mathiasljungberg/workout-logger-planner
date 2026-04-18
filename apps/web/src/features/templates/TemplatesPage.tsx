import { FormEvent, useEffect, useState } from "react";

import { Card } from "../../components/Card";
import { Page } from "../../components/Page";
import { api } from "../../lib/api/client";
import { Exercise, WorkoutTemplate } from "../../lib/api/types";

export function TemplatesPage() {
  const [templates, setTemplates] = useState<WorkoutTemplate[]>([]);
  const [exercises, setExercises] = useState<Exercise[]>([]);
  const [name, setName] = useState("");
  const [exerciseId, setExerciseId] = useState("");

  async function load() {
    const [templateData, exerciseData] = await Promise.all([
      api.get<WorkoutTemplate[]>("/templates"),
      api.get<Exercise[]>("/exercises"),
    ]);
    setTemplates(templateData);
    setExercises(exerciseData);
    if (!exerciseId && exerciseData[0]) {
      setExerciseId(exerciseData[0].id);
    }
  }

  useEffect(() => {
    load().catch(console.error);
  }, []);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!exerciseId || !name) return;
    await api.post("/templates", {
      name,
      description: null,
      exercises: [{ exercise_id: exerciseId, order_index: 0, target_sets: 3, target_reps: "8" }],
    });
    setName("");
    await load();
  }

  return (
    <Page title="Templates" description="Templates are reusable starting points. Sessions still snapshot performed work.">
      <div className="layout-two">
        <Card>
          <h3>New template</h3>
          <form className="stack" onSubmit={handleSubmit}>
            <label>
              Name
              <input value={name} onChange={(event) => setName(event.target.value)} placeholder="Upper body A" />
            </label>
            <label>
              First exercise
              <select value={exerciseId} onChange={(event) => setExerciseId(event.target.value)}>
                {exercises.map((exercise) => (
                  <option key={exercise.id} value={exercise.id}>
                    {exercise.name}
                  </option>
                ))}
              </select>
            </label>
            <button type="submit">Create template</button>
          </form>
        </Card>
        <div className="grid">
          {templates.map((template) => (
            <Card key={template.id}>
              <h3>{template.name}</h3>
              <ul className="list">
                {template.exercises.map((exercise) => (
                  <li key={exercise.id}>
                    {exercise.exercise_name}
                    {exercise.target_sets ? ` • ${exercise.target_sets} sets` : ""}
                    {exercise.target_reps ? ` • ${exercise.target_reps} reps` : ""}
                  </li>
                ))}
              </ul>
            </Card>
          ))}
        </div>
      </div>
    </Page>
  );
}


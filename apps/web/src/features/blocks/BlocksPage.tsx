import { FormEvent, useEffect, useState } from "react";

import { Card } from "../../components/Card";
import { Page } from "../../components/Page";
import { QueryBoundary } from "../../components/QueryBoundary";
import { useBlocks, useExercises } from "../../lib/api/queries";
import { useCreateBlock, useGeneratePlannedWorkouts } from "../../lib/api/mutations";

export function BlocksPage() {
  const { data: blocks = [], isLoading, error } = useBlocks();
  const { data: exercises = [] } = useExercises();
  const createBlock = useCreateBlock();
  const generatePlannedWorkouts = useGeneratePlannedWorkouts();

  const [name, setName] = useState("");
  const [exerciseId, setExerciseId] = useState("");

  useEffect(() => {
    if (!exerciseId && exercises[0]) {
      setExerciseId(exercises[0].id);
    }
  }, [exercises, exerciseId]);

  async function handleCreate(event: FormEvent) {
    event.preventDefault();
    if (!name || !exerciseId) return;
    await createBlock.mutateAsync({
      name,
      status: "draft",
      progression_rules: [
        {
          name: "Default progression",
          rule_type: "fixed_increment",
          config_json: { weight_increment: 2.5 },
        },
      ],
      workouts: [
        {
          name: "Day 1",
          week_index: 1,
          day_index: 1,
          exercises: [
            {
              exercise_id: exerciseId,
              order_index: 0,
              target_sets: 3,
              target_reps: "6-8",
              target_weight: 60,
              manual_override: false,
            },
          ],
        },
      ],
    });
    setName("");
  }

  async function generate(blockId: string) {
    const start = new Date().toISOString().slice(0, 10);
    await generatePlannedWorkouts.mutateAsync({
      blockId,
      payload: { start_date: start, weeks: 4 },
    });
  }

  return (
    <Page title="Blocks" description="Blocks author progression explicitly and expand into calendar instances.">
      <div className="layout-two">
        <Card>
          <h3>New block</h3>
          <form className="stack" onSubmit={handleCreate}>
            <label>
              Name
              <input value={name} onChange={(event) => setName(event.target.value)} placeholder="Hypertrophy Block" />
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
            <button type="submit" disabled={createBlock.isPending}>
              {createBlock.isPending ? "Creating..." : "Create block"}
            </button>
          </form>
        </Card>
        <QueryBoundary isLoading={isLoading} error={error} loadingLabel="Loading blocks...">
          <div className="grid">
            {blocks.map((block) => (
              <Card key={block.id}>
                <div className="row">
                  <h3>{block.name}</h3>
                  <span className="pill">{block.status}</span>
                </div>
                <p>{block.goal || "No goal set"}</p>
                <p>{block.progression_rules.length} progression rules</p>
                <p>{block.workouts.length} authored workouts</p>
                <button onClick={() => generate(block.id)} disabled={generatePlannedWorkouts.isPending}>
                  {generatePlannedWorkouts.isPending ? "Generating..." : "Generate 4 weeks"}
                </button>
              </Card>
            ))}
          </div>
        </QueryBoundary>
      </div>
    </Page>
  );
}

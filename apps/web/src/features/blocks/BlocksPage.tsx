import { FormEvent, useEffect, useState } from "react";

import { Card } from "../../components/Card";
import { Page } from "../../components/Page";
import { api } from "../../lib/api/client";
import { Exercise, TrainingBlock } from "../../lib/api/types";

export function BlocksPage() {
  const [blocks, setBlocks] = useState<TrainingBlock[]>([]);
  const [exercises, setExercises] = useState<Exercise[]>([]);
  const [name, setName] = useState("");
  const [exerciseId, setExerciseId] = useState("");

  async function load() {
    const [blockData, exerciseData] = await Promise.all([
      api.get<TrainingBlock[]>("/blocks"),
      api.get<Exercise[]>("/exercises"),
    ]);
    setBlocks(blockData);
    setExercises(exerciseData);
    if (!exerciseId && exerciseData[0]) {
      setExerciseId(exerciseData[0].id);
    }
  }

  useEffect(() => {
    load().catch(console.error);
  }, []);

  async function createBlock(event: FormEvent) {
    event.preventDefault();
    if (!name || !exerciseId) return;
    await api.post("/blocks", {
      name,
      status: "draft",
      progression_rules: [
        {
          name: "Default progression",
          rule_type: "double_progression",
          config_json: { reps_ceiling: 10, weight_increment: 2.5 },
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
            },
          ],
        },
      ],
    });
    setName("");
    await load();
  }

  async function generate(blockId: string) {
    const start = new Date().toISOString().slice(0, 10);
    await api.post(`/blocks/${blockId}/generate-planned-workouts`, { start_date: start, weeks: 4 });
  }

  return (
    <Page title="Blocks" description="Blocks author progression explicitly and expand into calendar instances.">
      <div className="layout-two">
        <Card>
          <h3>New block</h3>
          <form className="stack" onSubmit={createBlock}>
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
            <button type="submit">Create block</button>
          </form>
        </Card>
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
              <button onClick={() => generate(block.id)}>Generate 4 weeks</button>
            </Card>
          ))}
        </div>
      </div>
    </Page>
  );
}


import { FormEvent, useEffect, useState } from "react";

import { Card } from "../../components/Card";
import { Page } from "../../components/Page";
import { QueryBoundary } from "../../components/QueryBoundary";
import { useExercises, useTemplates } from "../../lib/api/queries";
import { useCreateTemplate } from "../../lib/api/mutations";

type TemplateDraftExercise = {
  exercise_id: string;
  order_index: number;
  notes: string;
  target_sets: string;
  target_reps: string;
  target_weight: string;
  target_duration_seconds: string;
  target_distance_meters: string;
  target_rpe: string;
};

function createDraftExercise(exerciseId = "", orderIndex = 0): TemplateDraftExercise {
  return {
    exercise_id: exerciseId,
    order_index: orderIndex,
    notes: "",
    target_sets: "",
    target_reps: "",
    target_weight: "",
    target_duration_seconds: "",
    target_distance_meters: "",
    target_rpe: "",
  };
}

function toOptionalNumber(value: string): number | null {
  if (value.trim() === "") {
    return null;
  }
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

export function TemplatesPage() {
  const { data: templates = [], isLoading, error } = useTemplates();
  const { data: exercises = [] } = useExercises();
  const createTemplate = useCreateTemplate();

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [draftExercises, setDraftExercises] = useState<TemplateDraftExercise[]>([]);
  const [formError, setFormError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  useEffect(() => {
    if (draftExercises.length === 0 && exercises[0]) {
      setDraftExercises([createDraftExercise(exercises[0].id, 0)]);
    }
  }, [exercises, draftExercises.length]);

  function addExerciseRow() {
    const fallbackExerciseId = exercises[0]?.id ?? "";
    setDraftExercises((current) => [...current, createDraftExercise(fallbackExerciseId, current.length)]);
  }

  function updateExerciseRow(index: number, key: keyof TemplateDraftExercise, value: string | number) {
    setDraftExercises((current) =>
      current.map((exercise, exerciseIndex) =>
        exerciseIndex === index ? { ...exercise, [key]: value } : exercise,
      ),
    );
  }

  function removeExerciseRow(index: number) {
    setDraftExercises((current) =>
      current
        .filter((_, exerciseIndex) => exerciseIndex !== index)
        .map((exercise, exerciseIndex) => ({ ...exercise, order_index: exerciseIndex })),
    );
  }

  function resetForm() {
    setName("");
    setDescription("");
    setFormError(null);
    setDraftExercises(exercises[0] ? [createDraftExercise(exercises[0].id, 0)] : []);
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFormError(null);
    setSuccessMessage(null);

    const cleanedName = name.trim();
    if (!cleanedName) {
      setFormError("Template name is required.");
      return;
    }
    if (draftExercises.length === 0) {
      setFormError("Add at least one exercise.");
      return;
    }
    if (draftExercises.some((exercise) => !exercise.exercise_id)) {
      setFormError("Each exercise row must have an exercise selected.");
      return;
    }

    try {
      await createTemplate.mutateAsync({
        name: cleanedName,
        description: description.trim() || null,
        exercises: draftExercises.map((exercise, index) => ({
          exercise_id: exercise.exercise_id,
          order_index: index,
          notes: exercise.notes.trim() || null,
          target_sets: toOptionalNumber(exercise.target_sets),
          target_reps: exercise.target_reps.trim() || null,
          target_weight: toOptionalNumber(exercise.target_weight),
          target_duration_seconds: toOptionalNumber(exercise.target_duration_seconds),
          target_distance_meters: toOptionalNumber(exercise.target_distance_meters),
          target_rpe: toOptionalNumber(exercise.target_rpe),
        })),
      });
      resetForm();
      setSuccessMessage("Template created.");
    } catch (caught) {
      setFormError(caught instanceof Error ? caught.message : "Failed to create template.");
    }
  }

  const saving = createTemplate.isPending;

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
              Description
              <textarea
                value={description}
                onChange={(event) => setDescription(event.target.value)}
                placeholder="Optional context, split, or warmup notes"
                rows={3}
              />
            </label>
            <div className="stack">
              <div className="row">
                <h4>Exercises</h4>
                <button type="button" onClick={addExerciseRow}>
                  Add exercise
                </button>
              </div>
              {draftExercises.map((exercise, index) => (
                <div key={`${exercise.exercise_id}-${index}`} className="card card--nested stack">
                  <div className="row">
                    <strong>Exercise {index + 1}</strong>
                    <button
                      type="button"
                      onClick={() => removeExerciseRow(index)}
                      disabled={draftExercises.length === 1}
                    >
                      Remove
                    </button>
                  </div>
                  <label>
                    Exercise
                    <select
                      value={exercise.exercise_id}
                      onChange={(event) => updateExerciseRow(index, "exercise_id", event.target.value)}
                    >
                      {exercises.map((item) => (
                        <option key={item.id} value={item.id}>
                          {item.name}
                        </option>
                      ))}
                    </select>
                  </label>
                  <div className="form-grid">
                    <label>
                      Sets
                      <input
                        inputMode="numeric"
                        value={exercise.target_sets}
                        onChange={(event) => updateExerciseRow(index, "target_sets", event.target.value)}
                        placeholder="3"
                      />
                    </label>
                    <label>
                      Reps
                      <input
                        value={exercise.target_reps}
                        onChange={(event) => updateExerciseRow(index, "target_reps", event.target.value)}
                        placeholder="8-10"
                      />
                    </label>
                    <label>
                      Weight
                      <input
                        inputMode="decimal"
                        value={exercise.target_weight}
                        onChange={(event) => updateExerciseRow(index, "target_weight", event.target.value)}
                        placeholder="60"
                      />
                    </label>
                    <label>
                      Duration sec
                      <input
                        inputMode="numeric"
                        value={exercise.target_duration_seconds}
                        onChange={(event) =>
                          updateExerciseRow(index, "target_duration_seconds", event.target.value)
                        }
                        placeholder="600"
                      />
                    </label>
                    <label>
                      Distance m
                      <input
                        inputMode="numeric"
                        value={exercise.target_distance_meters}
                        onChange={(event) =>
                          updateExerciseRow(index, "target_distance_meters", event.target.value)
                        }
                        placeholder="2000"
                      />
                    </label>
                    <label>
                      Target RPE
                      <input
                        inputMode="decimal"
                        value={exercise.target_rpe}
                        onChange={(event) => updateExerciseRow(index, "target_rpe", event.target.value)}
                        placeholder="8"
                      />
                    </label>
                  </div>
                  <label>
                    Notes
                    <textarea
                      value={exercise.notes}
                      onChange={(event) => updateExerciseRow(index, "notes", event.target.value)}
                      placeholder="Tempo, grip, setup, or substitutions"
                      rows={2}
                    />
                  </label>
                </div>
              ))}
            </div>
            {formError ? <p className="error">{formError}</p> : null}
            {successMessage ? <p>{successMessage}</p> : null}
            <button type="submit" disabled={saving || exercises.length === 0}>
              {saving ? "Creating..." : "Create template"}
            </button>
          </form>
        </Card>
        <QueryBoundary isLoading={isLoading} error={error} loadingLabel="Loading templates...">
          <div className="grid">
            {templates.map((template) => (
              <Card key={template.id}>
                <h3>{template.name}</h3>
                {template.description ? <p>{template.description}</p> : null}
                <ul className="list">
                  {template.exercises.map((exercise) => (
                    <li key={exercise.id}>
                      {exercise.exercise_name}
                      {exercise.target_sets ? ` • ${exercise.target_sets} sets` : ""}
                      {exercise.target_reps ? ` • ${exercise.target_reps} reps` : ""}
                      {exercise.target_weight ? ` • ${exercise.target_weight} kg` : ""}
                      {exercise.notes ? ` • ${exercise.notes}` : ""}
                    </li>
                  ))}
                </ul>
              </Card>
            ))}
          </div>
        </QueryBoundary>
      </div>
    </Page>
  );
}

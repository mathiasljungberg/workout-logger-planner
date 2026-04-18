from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.entities import Exercise, User
from app.services.auth import hash_password

DEFAULT_EXERCISES = [
    ("Back Squat", "strength", "reps_weight"),
    ("Bench Press", "strength", "reps_weight"),
    ("Deadlift", "strength", "reps_weight"),
    ("Pull Up", "strength", "reps_weight"),
    ("Running", "cardio", "distance"),
]


def seed_defaults(db: Session) -> None:
    user = db.scalar(select(User).where(User.username == settings.admin_username))
    if user is None:
        user = User(username=settings.admin_username, password_hash=hash_password(settings.admin_password))
        db.add(user)

    existing = {name for (name,) in db.execute(select(Exercise.name)).all()}
    for name, modality, measure_type in DEFAULT_EXERCISES:
        if name not in existing:
            db.add(
                Exercise(
                    name=name,
                    modality=modality,
                    default_measure_type=measure_type,
                )
            )

    db.commit()


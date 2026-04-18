from __future__ import annotations

from app.db.session import SessionLocal
from app.services.bootstrap import seed_defaults


def main() -> None:
    with SessionLocal() as db:
        seed_defaults(db)


if __name__ == "__main__":
    main()


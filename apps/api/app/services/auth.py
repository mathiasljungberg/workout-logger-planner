from __future__ import annotations

import hashlib

from itsdangerous import BadSignature, URLSafeSerializer

from app.core.config import settings


def hash_password(password: str) -> str:
    return hashlib.sha256(f"{settings.secret_key}:{password}".encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    return hash_password(password) == password_hash


def session_serializer() -> URLSafeSerializer:
    return URLSafeSerializer(settings.secret_key, salt="workout-tracker-session")


def sign_session(user_id: str) -> str:
    return session_serializer().dumps({"user_id": user_id})


def unsign_session(value: str) -> str | None:
    try:
        payload = session_serializer().loads(value)
    except BadSignature:
        return None
    return payload.get("user_id")


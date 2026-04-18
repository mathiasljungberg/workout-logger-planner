from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.session import get_db
from app.models.entities import User
from app.schemas.domain import AuthUser, LoginPayload
from app.services.auth import sign_session, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=AuthUser)
def login(payload: LoginPayload, response: Response, db: Session = Depends(get_db)) -> AuthUser:
    user = db.scalar(select(User).where(User.username == payload.username))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    response.set_cookie(
        key=settings.session_cookie_name,
        value=sign_session(user.id),
        httponly=True,
        samesite="lax",
        secure=settings.is_production,
    )
    return AuthUser.model_validate(user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response) -> Response:
    response.delete_cookie(settings.session_cookie_name)
    return response


@router.get("/me", response_model=AuthUser)
def me(user: User = Depends(get_current_user)) -> AuthUser:
    return AuthUser.model_validate(user)


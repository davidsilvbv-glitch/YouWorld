import uuid
from functools import wraps

from flask import jsonify, session
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from sqlalchemy import select

from .config import Config
from .db import db_session
from .models.auth_models import User, ProjectOwnership, SimulationOwnership, ReportOwnership


class AuthError(Exception):
    pass


def verify_google_token(token: str) -> dict:
    if not Config.GOOGLE_CLIENT_ID:
        raise AuthError("GOOGLE_CLIENT_ID no configurado")
    try:
        payload = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            Config.GOOGLE_CLIENT_ID,
        )
    except Exception as exc:
        raise AuthError(f"Token de Google inválido: {exc}") from exc
    if payload.get("iss") not in {"accounts.google.com", "https://accounts.google.com"}:
        raise AuthError("Issuer de Google inválido")
    return payload


def upsert_google_user(payload: dict) -> User:
    with db_session() as db:
        user = db.execute(select(User).where(User.google_sub == payload["sub"])).scalar_one_or_none()
        if user is None:
            user = User(
                user_id=f"usr_{uuid.uuid4().hex[:12]}",
                google_sub=payload["sub"],
                email=payload.get("email", ""),
                name=payload.get("name") or payload.get("email", "Usuario"),
                avatar_url=payload.get("picture"),
                email_verified=bool(payload.get("email_verified", False)),
            )
            db.add(user)
        else:
            user.email = payload.get("email", user.email)
            user.name = payload.get("name") or user.name
            user.avatar_url = payload.get("picture")
            user.email_verified = bool(payload.get("email_verified", user.email_verified))
        db.flush()
        db.refresh(user)
        return user


def login_user(user: User) -> None:
    session["user_id"] = user.user_id


def logout_user() -> None:
    session.pop("user_id", None)


def get_current_user() -> User | None:
    user_id = session.get("user_id")
    if not user_id:
        return None
    with db_session() as db:
        return db.execute(select(User).where(User.user_id == user_id)).scalar_one_or_none()


def require_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({"success": False, "error": "authentication_required"}), 401
        return fn(*args, **kwargs)
    return wrapper


def bind_project_to_user(project_id: str, user_id: str | None) -> None:
    if not user_id:
        return
    with db_session() as db:
        existing = db.execute(select(ProjectOwnership).where(ProjectOwnership.project_id == project_id)).scalar_one_or_none()
        if existing is None:
            db.add(ProjectOwnership(project_id=project_id, user_id=user_id))


def bind_simulation_to_user(simulation_id: str, project_id: str | None, user_id: str | None) -> None:
    if not user_id:
        return
    with db_session() as db:
        existing = db.execute(select(SimulationOwnership).where(SimulationOwnership.simulation_id == simulation_id)).scalar_one_or_none()
        if existing is None:
            db.add(SimulationOwnership(simulation_id=simulation_id, project_id=project_id, user_id=user_id))


def bind_report_to_user(report_id: str, simulation_id: str | None, project_id: str | None, user_id: str | None) -> None:
    if not user_id:
        return
    with db_session() as db:
        existing = db.execute(select(ReportOwnership).where(ReportOwnership.report_id == report_id)).scalar_one_or_none()
        if existing is None:
            db.add(ReportOwnership(report_id=report_id, simulation_id=simulation_id, project_id=project_id, user_id=user_id))


def user_owns_project(user_id: str | None, project_id: str) -> bool:
    if not user_id:
        return True
    with db_session() as db:
        ownership = db.execute(
            select(ProjectOwnership).where(
                ProjectOwnership.project_id == project_id,
                ProjectOwnership.user_id == user_id,
            )
        ).scalar_one_or_none()
        return ownership is not None


def user_owns_simulation(user_id: str | None, simulation_id: str) -> bool:
    if not user_id:
        return True
    with db_session() as db:
        ownership = db.execute(
            select(SimulationOwnership).where(
                SimulationOwnership.simulation_id == simulation_id,
                SimulationOwnership.user_id == user_id,
            )
        ).scalar_one_or_none()
        return ownership is not None


def user_owns_report(user_id: str | None, report_id: str) -> bool:
    if not user_id:
        return True
    with db_session() as db:
        ownership = db.execute(
            select(ReportOwnership).where(
                ReportOwnership.report_id == report_id,
                ReportOwnership.user_id == user_id,
            )
        ).scalar_one_or_none()
        return ownership is not None


def get_user_project_ids(user_id: str | None) -> list[str] | None:
    if not user_id:
        return None
    with db_session() as db:
        rows = db.execute(select(ProjectOwnership.project_id).where(ProjectOwnership.user_id == user_id)).all()
        return [row[0] for row in rows]


def get_user_simulation_ids(user_id: str | None) -> list[str] | None:
    if not user_id:
        return None
    with db_session() as db:
        rows = db.execute(select(SimulationOwnership.simulation_id).where(SimulationOwnership.user_id == user_id)).all()
        return [row[0] for row in rows]


def get_user_report_ids(user_id: str | None) -> list[str] | None:
    if not user_id:
        return None
    with db_session() as db:
        rows = db.execute(select(ReportOwnership.report_id).where(ReportOwnership.user_id == user_id)).all()
        return [row[0] for row in rows]

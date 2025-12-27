"""
Shared SQLAlchemy session factory for non-Flask contexts (e.g., MCP tools).

Why this exists:
- Flask-SQLAlchemy's `db.session` is request/app-context scoped.
- MCP tool execution happens outside Flask request handling, and may run concurrently.
- We therefore use a global `sessionmaker` factory initialized from the Flask app's engine,
  then create/close sessions per MCP tool invocation.
"""

from contextlib import contextmanager
from typing import Iterator, Optional

from sqlalchemy.orm import Session, sessionmaker

from api.app import db

SessionLocal: Optional[sessionmaker] = None


def init_session_factory(flask_app) -> None:
    """
    Initialize the global session factory using the Flask app's SQLAlchemy engine.

    Must be called once during process startup (e.g., from the ASGI entrypoint).
    """
    global SessionLocal
    with flask_app.app_context():
        engine = db.engine
        SessionLocal = sessionmaker(
            bind=engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )


@contextmanager
def session_scope() -> Iterator[Session]:
    """
    Provide a transactional scope around a series of operations.

    For MCP tools we typically only read, but we still ensure:
    - session is always closed
    - any unexpected exception triggers a rollback
    """
    if SessionLocal is None:
        raise RuntimeError(
            "SQLAlchemy session factory is not initialized. "
            "Call api.util.db_session.init_session_factory(flask_app) at startup."
        )

    session: Session = SessionLocal()
    try:
        yield session
        # Read-only usage: no commit
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

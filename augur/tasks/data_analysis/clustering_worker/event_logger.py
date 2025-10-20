"""
Event logger utilities for topic model versioning.

Default behavior: only file logs. When DB event logging is enabled by config or
environment variable, events are also persisted into augur_data.topic_model_event.

This module is intentionally lightweight and safe: DB failures never break the
main flow and always fall back to file logging only.
"""
import os
import json
from typing import Optional, Dict, Any

from augur.application.db.lib import get_session
from augur.application.db.models import TopicModelEvent
from augur.application.db.lib import get_value

# Optional import; only used when async mode is enabled
try:
    from augur.tasks.init.celery_app import celery_app as celery
except Exception:  # pragma: no cover
    celery = None


def _as_bool(value: Optional[str], default: bool = False) -> bool:
    if value is None:
        return default
    return str(value).lower() in ("1", "true", "t", "yes", "y")


def event_logging_enabled() -> bool:
    """Determine whether DB event logging is enabled (env overrides config)."""
    env_flag = os.getenv("AUGUR_ENABLE_DB_EVENT_LOGGING")
    if env_flag is not None:
        return _as_bool(env_flag, False)
    cfg_flag = get_value("Model_Management", "enable_db_event_logging")
    return _as_bool(str(cfg_flag) if cfg_flag is not None else None, False)


def event_logging_mode() -> str:
    """Return 'sync' or 'async'. Defaults to 'sync'."""
    env_mode = os.getenv("AUGUR_DB_EVENT_LOGGING_MODE")
    if env_mode:
        return env_mode.lower()
    cfg_mode = get_value("Model_Management", "db_event_logging_mode") or "sync"
    return str(cfg_mode).lower()


def log_event_file(logger, event: str, payload: Dict[str, Any]) -> None:
    """Always write a structured JSON event to file logger."""
    try:
        logger.info(json.dumps({"event": event, **payload}))
    except Exception:
        # Avoid raising from logging path
        pass


def _sanitize_payload(payload: Dict[str, Any], max_len: int = 4096) -> Dict[str, Any]:
    """Trim long string values and remove obviously sensitive keys."""
    SENSITIVE_KEYS = {"password", "token", "secret", "authorization"}
    safe: Dict[str, Any] = {}
    for k, v in payload.items():
        if k.lower() in SENSITIVE_KEYS:
            continue
        if isinstance(v, str) and len(v) > max_len:
            safe[k] = v[:max_len] + "..."
        else:
            safe[k] = v
    return safe


def log_event_db_sync(repo_id: Optional[int], model_id: Optional[str], event: str, level: str, payload: Dict[str, Any]) -> None:
    """Insert an event row into augur_data.topic_model_event synchronously."""
    try:
        with get_session() as session:
            session.add(TopicModelEvent(
                repo_id=repo_id,
                model_id=model_id,
                event=event,
                level=level,
                payload=_sanitize_payload(payload)
            ))
            session.commit()
    except Exception:
        # Do not propagate
        pass


def log_event_db_async(repo_id: Optional[int], model_id: Optional[str], event: str, level: str, payload: Dict[str, Any]) -> None:
    """Enqueue an async logging task if Celery is available; otherwise fallback to sync."""
    try:
        if celery is not None:
            celery.send_task("log_topic_model_event", kwargs={
                "repo_id": repo_id,
                "model_id": model_id,
                "event": event,
                "level": level,
                "payload": _sanitize_payload(payload)
            }, queue="events")
        else:
            log_event_db_sync(repo_id, model_id, event, level, payload)
    except Exception:
        # Do not propagate
        pass


def emit_event(logger, event: str, repo_id: Optional[int] = None, model_id: Optional[str] = None,
               level: str = "INFO", **payload) -> None:
    """Emit an event to file and optionally to DB based on configuration."""
    log_event_file(logger, event, {"repo_id": repo_id, "model_id": model_id, **payload})
    if not event_logging_enabled():
        return
    mode = event_logging_mode()
    if mode == "async":
        log_event_db_async(repo_id, model_id, event, level, payload)
    else:
        log_event_db_sync(repo_id, model_id, event, level, payload) 
import json

from sqlalchemy.orm import Session

from app.db.models.call_event_model import CallEvent
from app.db.models.call_session_model import CallSession


class CallEventRepository:
    def __init__(self, db: Session):
        self.db = db

    def log_event(self, event_type: str, payload: dict, session: CallSession | None = None) -> CallEvent:
        encoded_payload: dict | str = payload
        if self.db.bind and self.db.bind.dialect.name == "sqlite":
            encoded_payload = json.dumps(payload)

        event = CallEvent(
            call_session_id=session.id if session else None,
            event_type=event_type,
            payload_json=encoded_payload,
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

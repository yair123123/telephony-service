from sqlalchemy.orm import Session

from app.db.models.call_recording_model import CallRecording
from app.db.models.call_session_model import CallSession
from app.domain.enums.recording_kind import RecordingKind


class CallRecordingRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        session: CallSession,
        kind: RecordingKind,
        recording_url: str,
        provider_recording_id: str | None,
        duration_seconds: int | None,
    ) -> CallRecording:
        recording = CallRecording(
            call_session_id=session.id,
            kind=kind,
            provider_recording_id=provider_recording_id,
            recording_url=recording_url,
            duration_seconds=duration_seconds,
        )
        self.db.add(recording)
        self.db.commit()
        self.db.refresh(recording)
        return recording

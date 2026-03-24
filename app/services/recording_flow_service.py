from sqlalchemy import select
from sqlalchemy.orm import Session

from app.clients.core_client import CoreClient
from app.db.models.call_recording_model import CallRecording
from app.db.models.call_session_model import CallSession
from app.domain.enums.call_state import CallState
from app.domain.enums.recording_kind import RecordingKind
from app.domain.schemas.telephony_webhook import RecordingWebhookPayload
from app.repositories.call_event_repository import CallEventRepository
from app.repositories.call_recording_repository import CallRecordingRepository
from app.services.state_machine_service import StateMachineService
from app.services.telephony_response_builder import TelephonyResponseBuilder


class RecordingFlowService:
    def __init__(
        self,
        db: Session,
        client: CoreClient,
        state_machine: StateMachineService,
        recording_repo: CallRecordingRepository,
        event_repo: CallEventRepository,
        response_builder: TelephonyResponseBuilder,
    ):
        self.db = db
        self.client = client
        self.state_machine = state_machine
        self.recording_repo = recording_repo
        self.event_repo = event_repo
        self.response_builder = response_builder

    async def handle_recording(self, kind: RecordingKind, payload: RecordingWebhookPayload) -> str:
        session = self.db.query(CallSession).filter(CallSession.provider_call_id == payload.call_sid).first()
        if not session:
            return self.response_builder.say_and_hangup("Call session not found.")

        self.recording_repo.create(
            session=session,
            kind=kind,
            recording_url=payload.recording_url,
            provider_recording_id=payload.recording_sid,
            duration_seconds=payload.recording_duration,
        )
        self.event_repo.log_event(
            event_type=f"recording_{kind.value}",
            payload=payload.model_dump(by_alias=True),
            session=session,
        )

        if kind == RecordingKind.ORIGIN:
            self.state_machine.set_state(session, CallState.ASK_DESTINATION)
            return self.response_builder.say_and_record(
                "Please say your destination after the beep.", "/webhooks/voice/recordings/destination"
            )

        if kind == RecordingKind.DESTINATION:
            self.state_machine.set_state(session, CallState.ASK_NOTES)
            return self.response_builder.say_and_record(
                "Any additional notes for the driver?", "/webhooks/voice/recordings/notes"
            )

        self.state_machine.set_state(session, CallState.PROCESSING_ORDER)
        rows = self.db.execute(select(CallRecording).where(CallRecording.call_session_id == session.id)).scalars().all()
        recordings = {row.kind.value: row.recording_url for row in rows}
        result = await self.client.process_call_order(
            {
                "call_session_id": session.id,
                "from_phone": session.from_phone,
                "origin_recording_url": recordings.get(RecordingKind.ORIGIN.value),
                "destination_recording_url": recordings.get(RecordingKind.DESTINATION.value),
                "notes_recording_url": recordings.get(RecordingKind.NOTES.value),
            }
        )

        if result.can_confirm:
            if result.ride_id:
                session.ride_id = result.ride_id
                self.db.commit()
            self.state_machine.set_state(session, CallState.AWAIT_CONFIRMATION)
            message = result.summary_message or "Press 1 to confirm, 2 to re-record destination, 3 to re-record origin, 4 to re-record notes."
            return self.response_builder.say_and_gather_digits(message, "/webhooks/voice/dtmf/confirm")

        self.state_machine.set_state(session, CallState.FAILED)
        return self.response_builder.say_and_hangup(result.error_message or "We could not process your order.")

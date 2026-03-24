import pytest
from app.domain.enums.call_direction import CallDirection
from app.domain.enums.call_state import CallState
from app.domain.enums.recording_kind import RecordingKind
from app.domain.schemas.process_order_result import ProcessOrderResult
from app.domain.schemas.telephony_webhook import RecordingWebhookPayload
from app.repositories.call_event_repository import CallEventRepository
from app.repositories.call_recording_repository import CallRecordingRepository
from app.repositories.call_session_repository import CallSessionRepository
from app.services.recording_flow_service import RecordingFlowService
from app.services.state_machine_service import StateMachineService
from app.services.telephony_response_builder import TelephonyResponseBuilder


class FakeCore:
    async def process_call_order(self, payload):
        return ProcessOrderResult(can_confirm=True, ride_id=99, summary_message="Summary")


@pytest.mark.asyncio
async def test_state_transitions_recording_flow(db_session):
    session_repo = CallSessionRepository(db_session)
    session = session_repo.create("CA222", "0541111111", "0500000000", CallDirection.INBOUND)

    service = RecordingFlowService(
        db=db_session,
        client=FakeCore(),
        state_machine=StateMachineService(session_repo),
        recording_repo=CallRecordingRepository(db_session),
        event_repo=CallEventRepository(db_session),
        response_builder=TelephonyResponseBuilder(),
    )

    session_repo.update_state(session, CallState.ASK_ORIGIN)
    xml1 = await service.handle_recording(
        RecordingKind.ORIGIN,
        RecordingWebhookPayload(CallSid="CA222", RecordingUrl="http://rec/origin"),
    )
    assert "destination" in xml1.lower()

    session = session_repo.get_by_provider_call_id("CA222")
    assert session.current_state == CallState.ASK_DESTINATION

    xml2 = await service.handle_recording(
        RecordingKind.DESTINATION,
        RecordingWebhookPayload(CallSid="CA222", RecordingUrl="http://rec/dest"),
    )
    assert "notes" in xml2.lower()

    session = session_repo.get_by_provider_call_id("CA222")
    assert session.current_state == CallState.ASK_NOTES

    xml3 = await service.handle_recording(
        RecordingKind.NOTES,
        RecordingWebhookPayload(CallSid="CA222", RecordingUrl="http://rec/notes"),
    )
    assert "Gather" in xml3

    session = session_repo.get_by_provider_call_id("CA222")
    assert session.current_state == CallState.AWAIT_CONFIRMATION

import pytest

from app.domain.enums.call_direction import CallDirection
from app.domain.enums.call_state import CallState
from app.domain.schemas.telephony_webhook import DTMFWebhookPayload
from app.repositories.call_event_repository import CallEventRepository
from app.repositories.call_session_repository import CallSessionRepository
from app.services.dtmf_service import DTMFService
from app.services.state_machine_service import StateMachineService
from app.services.telephony_response_builder import TelephonyResponseBuilder


class FakeCore:
    async def confirm_ride(self, ride_id):
        return {"ok": True}

    async def cancel_searching_by_customer_phone(self, phone):
        return {"ok": True}


@pytest.mark.asyncio
async def test_dtmf_confirm_logic(db_session):
    repo = CallSessionRepository(db_session)
    session = repo.create("CA333", "0541234567", "0500000000", CallDirection.INBOUND)
    session.ride_id = 101
    repo.update_state(session, CallState.AWAIT_CONFIRMATION)

    service = DTMFService(
        db=db_session,
        client=FakeCore(),
        state_machine=StateMachineService(repo),
        event_repo=CallEventRepository(db_session),
        response_builder=TelephonyResponseBuilder(),
    )

    xml = await service.handle_confirm(DTMFWebhookPayload(CallSid="CA333", Digits="1"))
    assert "confirmed" in xml.lower()

    session = repo.get_by_provider_call_id("CA333")
    assert session.current_state == CallState.FINISHED

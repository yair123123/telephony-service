from sqlalchemy.orm import Session

from app.clients.core_client import CoreClient
from app.db.models.call_session_model import CallSession
from app.domain.enums.call_state import CallState
from app.domain.schemas.telephony_webhook import DTMFWebhookPayload
from app.repositories.call_event_repository import CallEventRepository
from app.services.state_machine_service import StateMachineService
from app.services.telephony_response_builder import TelephonyResponseBuilder


class DTMFService:
    def __init__(
        self,
        db: Session,
        client: CoreClient,
        state_machine: StateMachineService,
        event_repo: CallEventRepository,
        response_builder: TelephonyResponseBuilder,
    ):
        self.db = db
        self.client = client
        self.state_machine = state_machine
        self.event_repo = event_repo
        self.response_builder = response_builder

    async def handle_confirm(self, payload: DTMFWebhookPayload) -> str:
        session = self.db.query(CallSession).filter(CallSession.provider_call_id == payload.call_sid).first()
        if not session:
            return self.response_builder.say_and_hangup("Call session not found.")

        self.event_repo.log_event("dtmf_input", payload.model_dump(by_alias=True), session)
        digit = (payload.digits or "").strip()

        if session.current_state == CallState.AWAIT_CONFIRMATION:
            if digit == "1" and session.ride_id is not None:
                await self.client.confirm_ride(session.ride_id)
                self.state_machine.set_state(session, CallState.FINISHED)
                return self.response_builder.say_and_hangup("Your ride has been confirmed.")
            if digit == "2":
                self.state_machine.set_state(session, CallState.ASK_DESTINATION)
                return self.response_builder.say_and_record(
                    "Please re-record your destination after the beep.",
                    "/webhooks/voice/recordings/destination",
                )
            if digit == "3":
                self.state_machine.set_state(session, CallState.ASK_ORIGIN)
                return self.response_builder.say_and_record(
                    "Please re-record your origin after the beep.",
                    "/webhooks/voice/recordings/origin",
                )
            if digit == "4":
                self.state_machine.set_state(session, CallState.ASK_NOTES)
                return self.response_builder.say_and_record(
                    "Please re-record your notes after the beep.",
                    "/webhooks/voice/recordings/notes",
                )
            return self.response_builder.say_and_hangup("Invalid option.")

        if session.current_state == CallState.SEARCHING_DRIVER_MESSAGE:
            if digit == "1":
                await self.client.cancel_searching_by_customer_phone(session.from_phone)
                self.state_machine.set_state(session, CallState.FINISHED)
                return self.response_builder.say_and_hangup("Searching cancelled.")
            return self.response_builder.say_and_hangup("Still searching for a driver.")

        return self.response_builder.say_and_hangup("No DTMF action is available for this state.")

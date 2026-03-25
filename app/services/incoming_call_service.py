from app.clients.core_client import CoreClient
from app.config import Settings
from app.domain.enums.call_direction import CallDirection
from app.domain.enums.call_state import CallState
from app.domain.enums.routing_action import RoutingAction
from app.domain.schemas.telephony_webhook import VoiceWebhookPayload
from app.repositories.call_event_repository import CallEventRepository
from app.repositories.call_session_repository import CallSessionRepository
from app.services.call_bridge_service import CallBridgeService
from app.services.phone_normalizer import PhoneNormalizer
from app.services.state_machine_service import StateMachineService
from app.services.telephony_response_builder import TelephonyResponseBuilder


class IncomingCallService:
    def __init__(
        self,
        session_repo: CallSessionRepository,
        event_repo: CallEventRepository,
        core_client: CoreClient,
        phone_normalizer: PhoneNormalizer,
        response_builder: TelephonyResponseBuilder,
        bridge_service: CallBridgeService,
        state_machine: StateMachineService,
        settings: Settings,
    ):
        self.session_repo = session_repo
        self.event_repo = event_repo
        self.core_client = core_client
        self.phone_normalizer = phone_normalizer
        self.response_builder = response_builder
        self.bridge_service = bridge_service
        self.state_machine = state_machine
        self.settings = settings

    def _url(self, path: str) -> str:
        base = str(self.settings.base_url).rstrip("/")
        if not path.startswith("/"):
            path = f"/{path}"
        return f"{base}{path}"

    async def handle_incoming(self, payload: VoiceWebhookPayload) -> str:
        from_phone = self.phone_normalizer.normalize(payload.from_phone)
        to_phone = self.phone_normalizer.normalize(payload.to_phone)

        session = self.session_repo.get_by_provider_call_id(payload.call_sid)
        if not session:
            session = self.session_repo.create(
                provider_call_id=payload.call_sid,
                from_phone=from_phone,
                to_phone=to_phone,
                direction=CallDirection.INBOUND,
            )

        self.event_repo.log_event("incoming_call", payload.model_dump(by_alias=True), session)
        decision = await self.core_client.resolve_call_route(from_phone)
        self.session_repo.update_routing_action(session, decision.action)
        self.session_repo.attach_entities(session, decision.customer_id, decision.driver_id, decision.ride_id)

        if decision.action == RoutingAction.NEW_ORDER:
            self.state_machine.set_state(session, CallState.ASK_ORIGIN)
            return self.response_builder.say_and_record(
                "Welcome. Please say your pickup location after the beep.",
                self._url("/webhooks/voice/recordings/origin"),
            )

        if decision.action == RoutingAction.PLAY_SEARCHING_MESSAGE:
            self.state_machine.set_state(session, CallState.SEARCHING_DRIVER_MESSAGE)
            message = decision.message or "We are searching for a driver. Press 1 to cancel."
            return self.response_builder.say_and_gather_digits(
                message,
                self._url("/webhooks/voice/dtmf/confirm"),
            )

        if decision.action == RoutingAction.CONNECT_TO_DRIVER and decision.target_phone:
            self.state_machine.set_state(session, CallState.CONNECT_DRIVER)
            return self.bridge_service.bridge_to_phone(decision.target_phone)

        if decision.action == RoutingAction.CONNECT_TO_CUSTOMER and decision.target_phone:
            self.state_machine.set_state(session, CallState.CONNECT_CUSTOMER)
            return self.bridge_service.bridge_to_phone(decision.target_phone)

        if decision.action == RoutingAction.PLAY_NO_ACTIVE_RIDE:
            return self.response_builder.say_and_hangup(decision.message or "No active ride was found.")

        return self.response_builder.say_and_hangup(decision.message or "Thank you for calling.")
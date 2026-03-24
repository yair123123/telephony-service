from sqlalchemy.orm import Session

from app.db.models.call_session_model import CallSession
from app.domain.enums.call_direction import CallDirection
from app.domain.enums.call_session_status import CallSessionStatus
from app.domain.enums.call_state import CallState
from app.domain.enums.routing_action import RoutingAction


class CallSessionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_provider_call_id(self, provider_call_id: str) -> CallSession | None:
        return self.db.query(CallSession).filter(CallSession.provider_call_id == provider_call_id).first()

    def create(self, provider_call_id: str, from_phone: str, to_phone: str, direction: CallDirection) -> CallSession:
        session = CallSession(
            provider_call_id=provider_call_id,
            from_phone=from_phone,
            to_phone=to_phone,
            direction=direction,
            status=CallSessionStatus.ACTIVE,
            current_state=CallState.INCOMING,
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def update_state(self, session: CallSession, new_state: CallState) -> CallSession:
        session.current_state = new_state
        if new_state == CallState.FINISHED:
            session.status = CallSessionStatus.FINISHED
        if new_state == CallState.FAILED:
            session.status = CallSessionStatus.FAILED
        self.db.commit()
        self.db.refresh(session)
        return session

    def update_routing_action(self, session: CallSession, action: RoutingAction) -> CallSession:
        session.last_routing_action = action
        self.db.commit()
        self.db.refresh(session)
        return session

    def attach_entities(self, session: CallSession, customer_id: int | None, driver_id: int | None, ride_id: int | None) -> CallSession:
        session.customer_id = customer_id
        session.driver_id = driver_id
        session.ride_id = ride_id
        self.db.commit()
        self.db.refresh(session)
        return session

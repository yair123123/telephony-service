from dataclasses import dataclass

from app.db.models.call_session_model import CallSession
from app.domain.enums.call_state import CallState
from app.repositories.call_session_repository import CallSessionRepository


@dataclass(frozen=True)
class StateTransition:
    source: CallState
    target: CallState


class StateMachineService:
    def __init__(self, session_repo: CallSessionRepository):
        self.session_repo = session_repo

    def transition(self, session: CallSession, transition: StateTransition) -> CallSession:
        if session.current_state != transition.source:
            return session
        return self.session_repo.update_state(session, transition.target)

    def set_state(self, session: CallSession, target: CallState) -> CallSession:
        return self.session_repo.update_state(session, target)

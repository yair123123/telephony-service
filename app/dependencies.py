from fastapi import Depends
from sqlalchemy.orm import Session

from app.clients.core_client import CoreClient
from app.config import Settings, get_settings
from app.db.session import get_db_session
from app.repositories.call_event_repository import CallEventRepository
from app.repositories.call_recording_repository import CallRecordingRepository
from app.repositories.call_session_repository import CallSessionRepository
from app.services.call_bridge_service import CallBridgeService
from app.services.dtmf_service import DTMFService
from app.services.incoming_call_service import IncomingCallService
from app.services.phone_normalizer import PhoneNormalizer
from app.services.recording_flow_service import RecordingFlowService
from app.services.state_machine_service import StateMachineService
from app.services.telephony_response_builder import TelephonyResponseBuilder


def get_core_client(settings: Settings = Depends(get_settings)) -> CoreClient:
    return CoreClient(base_url=settings.core_backend_base_url, timeout_seconds=settings.core_backend_timeout_seconds)


def get_incoming_call_service(
    db: Session = Depends(get_db_session),
    core_client: CoreClient = Depends(get_core_client),
) -> IncomingCallService:
    session_repo = CallSessionRepository(db)
    response_builder = TelephonyResponseBuilder()
    return IncomingCallService(
        session_repo=session_repo,
        event_repo=CallEventRepository(db),
        core_client=core_client,
        phone_normalizer=PhoneNormalizer(),
        response_builder=response_builder,
        bridge_service=CallBridgeService(response_builder),
        state_machine=StateMachineService(session_repo),
    )


def get_recording_flow_service(
    db: Session = Depends(get_db_session),
    core_client: CoreClient = Depends(get_core_client),
) -> RecordingFlowService:
    session_repo = CallSessionRepository(db)
    return RecordingFlowService(
        db=db,
        client=core_client,
        state_machine=StateMachineService(session_repo),
        recording_repo=CallRecordingRepository(db),
        event_repo=CallEventRepository(db),
        response_builder=TelephonyResponseBuilder(),
    )


def get_dtmf_service(
    db: Session = Depends(get_db_session),
    core_client: CoreClient = Depends(get_core_client),
) -> DTMFService:
    session_repo = CallSessionRepository(db)
    return DTMFService(
        db=db,
        client=core_client,
        state_machine=StateMachineService(session_repo),
        event_repo=CallEventRepository(db),
        response_builder=TelephonyResponseBuilder(),
    )

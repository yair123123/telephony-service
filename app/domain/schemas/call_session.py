from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.domain.enums.call_direction import CallDirection
from app.domain.enums.call_session_status import CallSessionStatus
from app.domain.enums.call_state import CallState
from app.domain.enums.routing_action import RoutingAction


class CallSessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    provider_call_id: str
    from_phone: str
    to_phone: str
    direction: CallDirection
    current_state: CallState
    status: CallSessionStatus
    customer_id: int | None
    driver_id: int | None
    ride_id: int | None
    last_routing_action: RoutingAction | None
    created_at: datetime
    updated_at: datetime

from pydantic import BaseModel

from app.domain.enums.routing_action import RoutingAction


class RoutingDecision(BaseModel):
    action: RoutingAction
    message: str | None = None
    target_phone: str | None = None
    customer_id: int | None = None
    driver_id: int | None = None
    ride_id: int | None = None

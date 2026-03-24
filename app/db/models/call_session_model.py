from datetime import datetime

from sqlalchemy import DateTime, Enum, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.domain.enums.call_direction import CallDirection
from app.domain.enums.call_session_status import CallSessionStatus
from app.domain.enums.call_state import CallState
from app.domain.enums.routing_action import RoutingAction


class CallSession(Base):
    __tablename__ = "call_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    provider_call_id: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    from_phone: Mapped[str] = mapped_column(String(32), nullable=False)
    to_phone: Mapped[str] = mapped_column(String(32), nullable=False)
    direction: Mapped[CallDirection] = mapped_column(Enum(CallDirection), nullable=False)
    current_state: Mapped[CallState] = mapped_column(Enum(CallState), nullable=False, default=CallState.INCOMING)
    status: Mapped[CallSessionStatus] = mapped_column(Enum(CallSessionStatus), nullable=False, default=CallSessionStatus.ACTIVE)
    customer_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    driver_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ride_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_routing_action: Mapped[RoutingAction | None] = mapped_column(Enum(RoutingAction), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    recordings = relationship("CallRecording", back_populates="session")
    events = relationship("CallEvent", back_populates="session")

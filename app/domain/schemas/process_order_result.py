from pydantic import BaseModel


class ProcessOrderResult(BaseModel):
    can_confirm: bool
    summary_message: str | None = None
    ride_id: int | None = None
    error_message: str | None = None

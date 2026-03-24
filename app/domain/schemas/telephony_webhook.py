from pydantic import BaseModel, Field


class VoiceWebhookPayload(BaseModel):
    call_sid: str = Field(alias="CallSid")
    from_phone: str = Field(alias="From")
    to_phone: str = Field(alias="To")
    digits: str | None = Field(default=None, alias="Digits")


class RecordingWebhookPayload(BaseModel):
    call_sid: str = Field(alias="CallSid")
    recording_sid: str | None = Field(default=None, alias="RecordingSid")
    recording_url: str = Field(alias="RecordingUrl")
    recording_duration: int | None = Field(default=None, alias="RecordingDuration")


class DTMFWebhookPayload(BaseModel):
    call_sid: str = Field(alias="CallSid")
    digits: str | None = Field(default=None, alias="Digits")

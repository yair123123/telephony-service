from fastapi import APIRouter, Depends, Form, Response

from app.dependencies import get_recording_flow_service
from app.domain.enums.recording_kind import RecordingKind
from app.domain.schemas.telephony_webhook import RecordingWebhookPayload
from app.services.recording_flow_service import RecordingFlowService

router = APIRouter(prefix="/webhooks/voice/recordings", tags=["recordings"])


async def _handle(
    kind: RecordingKind,
    CallSid: str,
    RecordingUrl: str,
    service: RecordingFlowService,
    RecordingSid: str | None,
    RecordingDuration: int | None,
) -> Response:
    payload = RecordingWebhookPayload(
        CallSid=CallSid,
        RecordingSid=RecordingSid,
        RecordingUrl=RecordingUrl,
        RecordingDuration=RecordingDuration,
    )
    xml = await service.handle_recording(kind, payload)
    return Response(content=xml, media_type="application/xml")


@router.post("/origin")
async def origin(
    CallSid: str = Form(...),
    RecordingUrl: str = Form(...),
    RecordingSid: str | None = Form(default=None),
    RecordingDuration: int | None = Form(default=None),
    service: RecordingFlowService = Depends(get_recording_flow_service),
) -> Response:
    return await _handle(RecordingKind.ORIGIN, CallSid, RecordingUrl, service, RecordingSid, RecordingDuration)


@router.post("/destination")
async def destination(
    CallSid: str = Form(...),
    RecordingUrl: str = Form(...),
    RecordingSid: str | None = Form(default=None),
    RecordingDuration: int | None = Form(default=None),
    service: RecordingFlowService = Depends(get_recording_flow_service),
) -> Response:
    return await _handle(RecordingKind.DESTINATION, CallSid, RecordingUrl, service, RecordingSid, RecordingDuration)


@router.post("/notes")
async def notes(
    CallSid: str = Form(...),
    RecordingUrl: str = Form(...),
    RecordingSid: str | None = Form(default=None),
    RecordingDuration: int | None = Form(default=None),
    service: RecordingFlowService = Depends(get_recording_flow_service),
) -> Response:
    return await _handle(RecordingKind.NOTES, CallSid, RecordingUrl, service, RecordingSid, RecordingDuration)

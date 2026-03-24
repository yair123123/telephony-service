from fastapi import APIRouter, Depends, Form, Response

from app.dependencies import get_incoming_call_service
from app.domain.schemas.telephony_webhook import VoiceWebhookPayload
from app.services.incoming_call_service import IncomingCallService

router = APIRouter(prefix="/webhooks/voice", tags=["voice"])


@router.post("/incoming")
async def incoming_call(
    CallSid: str = Form(...),
    From: str = Form(...),
    To: str = Form(...),
    service: IncomingCallService = Depends(get_incoming_call_service),
) -> Response:
    payload = VoiceWebhookPayload(CallSid=CallSid, From=From, To=To)
    xml = await service.handle_incoming(payload)
    return Response(content=xml, media_type="application/xml")

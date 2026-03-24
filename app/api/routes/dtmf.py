from fastapi import APIRouter, Depends, Form, Response

from app.dependencies import get_dtmf_service
from app.domain.schemas.telephony_webhook import DTMFWebhookPayload
from app.services.dtmf_service import DTMFService

router = APIRouter(prefix="/webhooks/voice/dtmf", tags=["dtmf"])


@router.post("/confirm")
async def confirm(
    CallSid: str = Form(...),
    Digits: str | None = Form(default=None),
    service: DTMFService = Depends(get_dtmf_service),
) -> Response:
    payload = DTMFWebhookPayload(CallSid=CallSid, Digits=Digits)
    xml = await service.handle_confirm(payload)
    return Response(content=xml, media_type="application/xml")

from app.services.telephony_response_builder import TelephonyResponseBuilder


class CallBridgeService:
    def __init__(self, response_builder: TelephonyResponseBuilder):
        self.response_builder = response_builder

    def bridge_to_phone(self, number: str, caller_id: str | None = None) -> str:
        return self.response_builder.dial_number(number, caller_id=caller_id)

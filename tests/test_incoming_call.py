from app.domain.enums.routing_action import RoutingAction
from app.domain.schemas.routing_decision import RoutingDecision


class FakeCoreNewOrder:
    async def resolve_call_route(self, phone: str):
        return RoutingDecision(action=RoutingAction.NEW_ORDER)



def test_incoming_call_new_order(client):
    test_client, _ = client
    test_client.app.dependency_overrides.clear()

    from app.dependencies import get_core_client

    test_client.app.dependency_overrides[get_core_client] = lambda: FakeCoreNewOrder()

    response = test_client.post(
        "/webhooks/voice/incoming",
        data={"CallSid": "CA111", "From": "+972541234567", "To": "+972500000000"},
    )
    assert response.status_code == 200
    assert "<Record" in response.text
    assert "/webhooks/voice/recordings/origin" in response.text

from app.services.telephony_response_builder import TelephonyResponseBuilder


def test_xml_builder_basic():
    builder = TelephonyResponseBuilder()
    assert "<Say>Hello</Say>" in builder.say("Hello")
    assert "<Hangup" in builder.say_and_hangup("bye")
    assert "<Record" in builder.say_and_record("msg", "/x")
    assert "<Gather" in builder.say_and_gather_digits("msg", "/x")
    assert "<Dial" in builder.dial_number("+123")

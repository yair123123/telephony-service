from xml.etree.ElementTree import Element, SubElement, tostring


class TelephonyResponseBuilder:
    def _to_xml(self, response: Element) -> str:
        return tostring(response, encoding="unicode")

    def say(self, message: str) -> str:
        response = Element("Response")
        say = SubElement(response, "Say")
        say.text = message
        return self._to_xml(response)

    def say_and_hangup(self, message: str) -> str:
        response = Element("Response")
        say = SubElement(response, "Say")
        say.text = message
        SubElement(response, "Hangup")
        return self._to_xml(response)

    def say_and_record(self, message: str, action_url: str, max_length: int = 8) -> str:
        response = Element("Response")
        say = SubElement(response, "Say")
        say.text = message
        SubElement(response, "Record", action=action_url, maxLength=str(max_length), method="POST")
        return self._to_xml(response)

    def say_and_gather_digits(self, message: str, action_url: str, num_digits: int = 1) -> str:
        response = Element("Response")
        gather = SubElement(response, "Gather", action=action_url, numDigits=str(num_digits), method="POST")
        say = SubElement(gather, "Say")
        say.text = message
        return self._to_xml(response)

    def dial_number(self, number: str, caller_id: str | None = None) -> str:
        response = Element("Response")
        attributes = {"callerId": caller_id} if caller_id else {}
        dial = SubElement(response, "Dial", **attributes)
        number_el = SubElement(dial, "Number")
        number_el.text = number
        return self._to_xml(response)

    def redirect(self, url: str) -> str:
        response = Element("Response")
        redirect = SubElement(response, "Redirect", method="POST")
        redirect.text = url
        return self._to_xml(response)

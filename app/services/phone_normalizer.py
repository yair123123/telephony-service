import re


class PhoneNormalizer:
    @staticmethod
    def normalize(phone: str) -> str:
        value = re.sub(r"[\s\-()]+", "", phone or "")
        if not value:
            return ""
        if value.startswith("+"):
            value = value[1:]

        if value.startswith("972"):
            remainder = value[3:]
            if remainder.startswith("0"):
                remainder = remainder[1:]
            return f"0{remainder}"

        if value.startswith("0"):
            return value

        if len(value) in {8, 9, 10}:
            return f"0{value}" if not value.startswith("0") else value

        return value

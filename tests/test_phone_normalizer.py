from app.services.phone_normalizer import PhoneNormalizer


def test_phone_normalization_israeli_formats():
    assert PhoneNormalizer.normalize("+972-54-123-4567") == "0541234567"
    assert PhoneNormalizer.normalize("972541234567") == "0541234567"
    assert PhoneNormalizer.normalize("0541234567") == "0541234567"
    assert PhoneNormalizer.normalize("(054) 123 4567") == "0541234567"

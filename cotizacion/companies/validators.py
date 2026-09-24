from django.core.exceptions import ValidationError


def normalize_rut(value):
    return "".join(char for char in str(value).strip().upper() if char.isalnum())


def _check_digit(body):
    total = 0
    multiplier = 2
    for char in reversed(body):
        total += int(char) * multiplier
        multiplier = 2 if multiplier == 7 else multiplier + 1
    remainder = total % 11
    result = 11 - remainder
    if result == 11:
        return "0"
    if result == 10:
        return "K"
    return str(result)


def format_rut(body, verifier):
    grouped = ""
    for index, char in enumerate(reversed(body)):
        if index and index % 3 == 0:
            grouped = "." + grouped
        grouped = char + grouped
    return f"{grouped}-{verifier}"


def validate_rut(value):
    raw = normalize_rut(value)
    if len(raw) < 2 or not raw[:-1].isdigit() or raw[-1] not in "0123456789K":
        raise ValidationError("Ingresa un RUT válido.")
    body, verifier = raw[:-1], raw[-1]
    if _check_digit(body) != verifier:
        raise ValidationError("El RUT ingresado no es válido.")
    return format_rut(body, verifier)
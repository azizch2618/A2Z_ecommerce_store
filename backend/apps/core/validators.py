"""Australian business validators."""
import re

from django.core.exceptions import ValidationError

AU_STATES = frozenset({"NSW", "VIC", "QLD", "SA", "WA", "TAS", "NT", "ACT"})
POSTCODE_RE = re.compile(r"^\d{4}$")
ABN_RE = re.compile(r"^\d{11}$")


def validate_australian_postcode(value: str) -> None:
    if not POSTCODE_RE.match(value):
        raise ValidationError("Postcode must be a 4-digit Australian postcode.")


def validate_australian_state(value: str) -> None:
    if value not in AU_STATES:
        raise ValidationError(f"State must be one of: {', '.join(sorted(AU_STATES))}.")


def validate_abn(value: str) -> None:
    if not ABN_RE.match(value):
        raise ValidationError("ABN must be exactly 11 digits.")

    weights = [10, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
    digits = [int(d) - 1 if i == 0 else int(d) for i, d in enumerate(value)]
    total = sum(d * w for d, w in zip(digits, weights, strict=True))
    if total % 89 != 0:
        raise ValidationError("Invalid ABN checksum.")

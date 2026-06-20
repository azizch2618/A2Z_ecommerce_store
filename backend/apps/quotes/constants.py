"""Quotation & sales workflow constants."""
from django.conf import settings


def quote_approval_threshold_cents() -> int:
    return int(getattr(settings, "QUOTE_APPROVAL_THRESHOLD_CENTS", 500_000))

DEFAULT_QUOTE_TERMS = """Payment terms: Net 30 days from invoice date.
Prices are in AUD and include GST where applicable.
Quote valid until the expiry date shown above.
Goods remain property of A2Z Tools until paid in full."""

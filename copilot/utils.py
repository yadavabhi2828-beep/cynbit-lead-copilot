from __future__ import annotations

import re

_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_PHONE = re.compile(r"(?<!\d)(?:\+?\d[\d\s-]{8,}\d)(?!\d)")


def mask_pii(text: str) -> str:
    """Mask e-mail addresses and phone numbers before anything is logged."""
    return _PHONE.sub("[phone]", _EMAIL.sub("[email]", text))

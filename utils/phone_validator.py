"""
Uzbek phone number validator.
Uses phonenumbers library for strict validation.
"""

import re
import logging
from typing import Optional

import phonenumbers
from phonenumbers import NumberParseException

logger = logging.getLogger(__name__)


def validate_uzbek_phone(phone: str) -> Optional[str]:
    """
    Validate and normalize an Uzbek phone number.

    Accepted formats:
        +998901234567
        998901234567
        0901234567
        +998 90 123 45 67
        +998-90-123-45-67

    Returns:
        E.164 formatted phone number (+998XXXXXXXXX) if valid,
        None if invalid.
    """
    # Remove spaces, dashes, parentheses
    clean = re.sub(r"[\s\-\(\)]", "", phone.strip())

    # Handle short format: 0901234567 → +998901234567
    if re.match(r"^0\d{9}$", clean):
        clean = "+998" + clean[1:]
    elif re.match(r"^998\d{9}$", clean):
        clean = "+" + clean
    elif not clean.startswith("+"):
        clean = "+" + clean

    try:
        parsed = phonenumbers.parse(clean, "UZ")
        if (
            phonenumbers.is_valid_number(parsed)
            and phonenumbers.region_code_for_number(parsed) == "UZ"
        ):
            return phonenumbers.format_number(
                parsed, phonenumbers.PhoneNumberFormat.E164
            )
    except NumberParseException:
        pass
    except Exception as e:
        logger.warning("Phone validation error: %s", e)

    return None

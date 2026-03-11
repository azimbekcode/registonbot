"""
Referral code generator utility.
"""

import secrets
import string


def generate_referral_code(length: int = 10) -> str:
    """
    Generate a cryptographically secure referral code.

    Args:
        length: Length of the referral code (default 10)

    Returns:
        Random alphanumeric string
    """
    chars = string.ascii_letters + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))

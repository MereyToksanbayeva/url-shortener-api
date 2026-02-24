import secrets
import string

ALPHABET = string.ascii_letters + string.digits  # a-zA-Z0-9


def generate_code(length: int = 7) -> str:
    """
    Generate a random short code for shortened URLs.
    7 chars ~ 62^7 combinations (very large).
    """
    return "".join(secrets.choice(ALPHABET) for _ in range(length))

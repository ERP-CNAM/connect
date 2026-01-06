import os

from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

CONNECT_API_KEY = os.getenv("CONNECT_API_KEY")
assert CONNECT_API_KEY is not None, "CONNECT_API_KEY environment variable is not set"


def validate_api_key(api_key: str) -> bool:
    """
    Validates the provided API key against the configured CONNECT_API_KEY.

    Args:
        api_key: The API key to validate

    Returns:
        True if the API key is valid, False otherwise.
    """
    if api_key != CONNECT_API_KEY:
        return False

    return True


def get_api_key() -> str:
    """
    Returns the configured CONNECT_API_KEY.

    Returns:
        The API key as a string.
    """
    return CONNECT_API_KEY

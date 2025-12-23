import os

from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv(dotenv_path=".env")

CONNECT_API_KEY = os.getenv("CONNECT_API_KEY")
assert CONNECT_API_KEY is not None, "CONNECT_API_KEY environment variable is not set"


def validate_api_key(api_key: str) -> None:
    """
    Validates the provided API key against the configured CONNECT_API_KEY.

    Args:
        api_key: The API key to validate

    Raises:
        HTTPException: If the API key is invalid (401 Unauthorized)
    """
    if api_key != CONNECT_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

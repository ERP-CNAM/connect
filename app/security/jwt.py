import os

import jwt
from dotenv import load_dotenv

from app.models.connect_body import UserData

load_dotenv(dotenv_path=".env")

CONNECT_JWT_SECRET = os.getenv("CONNECT_JWT_SECRET")
assert CONNECT_JWT_SECRET is not None, (
    "CONNECT_JWT_SECRET environment variable is not set"
)


def validate_jwt(token: str) -> UserData:
    """
    Validates the provided JWT token using the configured CONNECT_JWT_SECRET.

    Args:
        token: The JWT token to validate

    Raises:
        jwt.ExpiredSignatureError If the JWT has expired
        jwt.InvalidTokenError If the JWT is invalid
        pydantic.ValidationError If the JWT payload cannot be parsed

    returns:
        Decoded UserData
    """

    user_data = jwt.decode(token, CONNECT_JWT_SECRET, algorithms=["HS256"])

    return UserData(**user_data)

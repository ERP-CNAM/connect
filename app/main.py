import os

from dotenv import load_dotenv
from fastapi import FastAPI, status

from app.models.register_body import RegisterBody, RegisterBodyPublic
from app.security.key import validate_api_key

load_dotenv(dotenv_path=".env")

CONNECT_VERSION = os.getenv("CONNECT_VERSION")
assert CONNECT_VERSION is not None, "CONNECT_VERSION environment variable is not set"

api = FastAPI()
registered_services: list[RegisterBodyPublic] = list()


@api.get("/ping", status_code=status.HTTP_200_OK)
def ping():
    return {}


@api.post("/register")
def register(body: RegisterBody, status=status.HTTP_202_ACCEPTED):
    is_valid, error_message = validate_api_key(body.apiKey)
    if not is_valid:
        return {
            "Error while validating API key": error_message
        }, status.HTTP_401_UNAUTHORIZED

    body_filtered = RegisterBodyPublic(
        name=body.name,
        description=body.description,
        version=body.version,
        routes=body.routes,
    )

    # TODO : check for duplicates
    for service in registered_services:
        if (
            service.name == body_filtered.name
            and service.version == body_filtered.version
        ):
            return {
                "Error while registering service": "Service with this name and version already registered"
            }, status.HTTP_409_CONFLICT

    registered_services.append(body_filtered)

    return {"message": "Service registered successfully"}


@api.get("/services")
def services():
    return registered_services

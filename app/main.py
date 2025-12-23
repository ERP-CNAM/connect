import os

from dotenv import load_dotenv
from fastapi import FastAPI, Request, status

from app.models.register_body import RegisterBodyIn, RegisterBodyOut, RegisterBodyStored
from app.security.key import validate_api_key

load_dotenv(dotenv_path=".env")

CONNECT_VERSION = os.getenv("CONNECT_VERSION")
assert CONNECT_VERSION is not None, "CONNECT_VERSION environment variable is not set"

api = FastAPI()
registered_services: list[RegisterBodyStored] = list()


@api.get("/ping", status_code=status.HTTP_200_OK)
def ping():
    return {}


@api.post("/register")
def register(request: Request, body: RegisterBodyIn, status=status.HTTP_202_ACCEPTED):
    is_valid, error_message = validate_api_key(body.apiKey)
    if not is_valid:
        return {
            "Error while validating API key": error_message
        }, status.HTTP_401_UNAUTHORIZED

    # TODO : check for duplicates
    for service in registered_services:
        if service.name == body.name and service.version == body.version:
            return {
                "Error while registering service": "Service with this name and version already registered"
            }, status.HTTP_409_CONFLICT

    service_ip = request.client.host

    body_stored = RegisterBodyStored(
        name=body.name,
        description=body.description,
        version=body.version,
        routes=body.routes,
        listeningPort=body.listeningPort,
        ip=service_ip,
    )

    registered_services.append(body_stored)

    return {"message": "Service registered successfully"}


@api.get("/services")
def services():
    return [
        RegisterBodyOut(
            name=service.name,
            description=service.description,
            version=service.version,
            routes=service.routes,
        )
        for service in registered_services
    ]

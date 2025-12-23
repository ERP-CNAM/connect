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
def register(body: RegisterBody):
    validate_api_key(body.apiKey)

    body_filtered = RegisterBodyPublic(
        name=body.name,
        description=body.description,
        version=body.version,
        routes=body.routes,
    )

    # TODO : check for duplicates

    registered_services.append(body_filtered)

    return {}


@api.get("/services")
def services():
    return registered_services

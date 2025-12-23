import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status

from app.models.register_body import RegisterBody, RegisterBodyPublic

load_dotenv(dotenv_path=".env")

CONNECT_API_KEY = os.getenv("CONNECT_API_KEY")
CONNECT_VERSION = os.getenv("CONNECT_VERSION")
assert CONNECT_API_KEY is not None and CONNECT_VERSION is not None, (
    "Environment variable is not set"
)

api = FastAPI()
registered_services: list[RegisterBodyPublic] = list()


@api.get("/ping", status_code=status.HTTP_200_OK)
def ping():
    return {}


@api.post("/register")
def register(body: RegisterBody):
    valid_key = body.apiKey == CONNECT_API_KEY
    if not valid_key:
        raise HTTPException(status_code=401)

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

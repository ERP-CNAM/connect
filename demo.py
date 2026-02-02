import logging
import os
from typing import Any

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

load_dotenv(dotenv_path="demo.env")
APP_NAME = os.getenv("APP_NAME", "Stein Files")
APP_DESCRIPTION = os.getenv("APP_DESCRIPTION", "A simple file management utility")
APP_VERSION = os.getenv("APP_VERSION", "2026.2")
app_port_str = os.getenv("APP_PORT", "")
APP_PORT = int(app_port_str) if app_port_str.isdecimal() else 8000
CONNECT_HOST = os.getenv("CONNECT_HOST", "localhost:8001")
CONNECT_API_KEY = os.getenv("CONNECT_API_KEY", "changethis")
HTTPS = bool(os.getenv("HTTPS"))
OVERRIDE_IP = os.getenv("OVERRIDE_IP")

logger = logging.getLogger(APP_NAME)


files = [
    {
        "path": "/mnt/e",
        "content": [
            {"path": "folder1", "content": [{"path": "test"}]},
            {"path": "emptyFolder", "content": []},
        ],
    }
]


class UserData(BaseModel):
    exp: int
    userId: str
    permission: int


class ConnectServiceIn(BaseModel):
    apiKey: str
    debug: bool
    userData: UserData | dict
    payload: Any


class CreateFilePayload(BaseModel):
    filename: str


class CreateFileBody(ConnectServiceIn):
    payload: CreateFilePayload


class ConnectServiceOut(BaseModel):
    success: bool
    message: str
    payload: Any


def check_service_status():
    endpoint = f"https://{CONNECT_HOST}" if HTTPS else f"http://{CONNECT_HOST}/ping"
    response = requests.get(endpoint)
    if response.status_code != status.HTTP_200_OK:
        raise Exception(
            f"{CONNECT_HOST} was expected to respond with {status.HTTP_200_OK}. Actual: {response.status_code}: {response.json()}"
        )


def register_service():
    body = {
        "name": APP_NAME,
        "description": APP_DESCRIPTION,
        "version": APP_VERSION,
        "routes": [
            {"path": "files", "method": "GET", "permission": 4},
            {"path": "files/new", "method": "POST", "permission": 6},
        ],
        "listeningPort": APP_PORT,
        "apiKey": CONNECT_API_KEY,
    }
    if OVERRIDE_IP is not None:
        body["overrideIp"] = OVERRIDE_IP
    response = requests.post(f"http://{CONNECT_HOST}/register", json=body)
    if not response.status_code == status.HTTP_202_ACCEPTED:
        logger.error(
            f"Could not register on Connect: {response.json()} ({response.status_code})"
        )


app = FastAPI(on_startup=[check_service_status, register_service])


@app.get("/files")
def get_files():
    return ConnectServiceOut(
        success=True,
        payload=files,
        message="Returning user files",
    )


@app.post("/files/new")
def create_file(body: CreateFileBody):
    filename = body.payload.filename
    files.append({"path": filename})
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=ConnectServiceOut(
            success=True, payload=files, message=f"You created {filename}"
        ).model_dump(),
    )

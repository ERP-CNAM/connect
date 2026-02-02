import logging
import os

import jwt
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

load_dotenv(dotenv_path="demo.env")
APP_NAME = os.getenv("APP_NAME", "Stein Files")
APP_DESCRIPTION = os.getenv("APP_DESCRIPTION", "A simple file management utility")
APP_VERSION = os.getenv("APP_VERSION", "2026.2")
app_port_str = os.getenv("APP_PORT", "")
APP_PORT = int(app_port_str) if app_port_str.isdecimal() else 8001
CONNECT_HOST = os.getenv("CONNECT_HOST", "localhost:8000")
CONNECT_API_KEY = os.getenv("CONNECT_API_KEY", "changethis")
HTTPS = bool(os.getenv("HTTPS"))
OVERRIDE_IP = os.getenv("OVERRIDE_IP")

logger = logging.getLogger(APP_NAME)


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
        "routes": [],
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
    print("Test")


api = FastAPI(on_startup=[check_service_status(), register_service()])


@api.get("/ping")
def ping():
    return JSONResponse(status_code=status.HTTP_200_OK, content={})

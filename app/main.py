import os
from time import time

import jwt
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.logger import log_and_prepare
from app.match_route import match_route
from app.models.connect_body import (
    ConnectClientIn,
    ConnectClientOut,
    ConnectServiceIn,
    ConnectServiceOut,
    ConnectStatus,
)
from app.models.connect_log import FixedLogData
from app.models.register_body import RegisterBodyIn, RegisterBodyOut, RegisterBodyStored
from app.security.jwt import validate_jwt
from app.security.key import get_api_key, validate_api_key

load_dotenv(dotenv_path=".env")

CONNECT_VERSION = os.getenv("CONNECT_VERSION")
assert CONNECT_VERSION is not None, "CONNECT_VERSION environment variable is not set"

api = FastAPI()
registered_services: list[RegisterBodyStored] = list()


@api.get("/ping")
def ping():
    return JSONResponse(status_code=status.HTTP_200_OK, content={})


@api.post("/register")
def register(request: Request, body: RegisterBodyIn):
    is_valid = validate_api_key(body.apiKey)
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid API key"},
        )
    replaced = False
    for index, service in enumerate(registered_services):
        if service.name == body.name:
            registered_services.pop(index)
            replaced = True
            break

    service_ip = getattr(body, "overrideIp", None) or request.client.host

    body_stored = RegisterBodyStored(
        name=body.name,
        description=body.description,
        version=body.version,
        routes=body.routes,
        listeningPort=body.listeningPort,
        ip=service_ip,
    )

    registered_services.append(body_stored)

    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={
            "detail": f"Replaced existing {body.name} with version {body.version}"
            if replaced
            else f"Registered {body.name} version {body.version}"
        },
    )


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


@api.api_route(
    "/connect",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD", "TRACE"],
    response_model=ConnectClientOut,
)
def connect(request: Request, body: ConnectClientIn):
    # Timestamp in
    timestamp_in = time() * 1000

    # Prepare data
    log_data = FixedLogData(
        timestamp_in=timestamp_in,
        body=body,
        method=request.method,
        service_version="",
    )

    data_out: ConnectClientOut = ConnectClientOut(
        success=False,
        id=0,
        status=ConnectStatus.SUCCESS,
        message="",
        payload={},
    )

    debug = body.debug

    token = None
    user_data = {}

    # JWT in Authorization header
    auth = request.headers.get("Authorization")
    if auth and auth.lower().startswith("bearer "):
        token = auth.split(" ", 1)[1]

    # JWT in cookie
    if not token:
        token = request.cookies.get("token")

    # Check JWT validity
    if token is not None:
        try:
            user_data = validate_jwt(token)
        except jwt.ExpiredSignatureError:
            data_out.status = ConnectStatus.UNREGISTERED
            data_out.message = "Expired JWT"
            return log_and_prepare(
                log_data=log_data,
                data_out=data_out,
                user_data=user_data,
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        except jwt.InvalidTokenError:
            data_out.status = ConnectStatus.UNREGISTERED
            data_out.message = "Invalid JWT"
            return log_and_prepare(
                log_data=log_data,
                data_out=data_out,
                user_data=user_data,
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        except ValidationError as e:
            data_out.status = ConnectStatus.UNREGISTERED
            data_out.message = f"JWT payload invalid ({e})"
            return log_and_prepare(
                log_data=log_data,
                data_out=data_out,
                user_data=user_data,
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
    user_permission = 0 if not user_data else user_data.permission

    # Check API key
    api_key_access = validate_api_key(body.apiKey)

    # Check service
    matched_service = None
    for service in registered_services:
        if service.name == body.serviceName:
            matched_service = service
            log_data.service_version = service.version
            break
    if matched_service is None:
        data_out.status = ConnectStatus.UNREGISTERED
        data_out.message = "Service not registered"
        return log_and_prepare(
            log_data=log_data,
            data_out=data_out,
            user_data=user_data,
            status_code=status.HTTP_404_NOT_FOUND,
        )

    # Check path/route
    matched_route = None
    method_valid = False
    for route in matched_service.routes:
        if match_route(route.path, body.path):
            matched_route = route
            if route.method == request.method:
                method_valid = True
                break
    if matched_route is None:
        data_out.status = ConnectStatus.UNREGISTERED
        data_out.message = "Path not in service"
        return log_and_prepare(
            log_data=log_data,
            data_out=data_out,
            user_data=user_data,
            status_code=status.HTTP_404_NOT_FOUND,
        )

    # Check method
    if not method_valid:
        data_out.status = ConnectStatus.UNREGISTERED
        data_out.message = f"Method {request.method} wrongfully used on route"
        return log_and_prepare(
            log_data=log_data,
            data_out=data_out,
            user_data=user_data,
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    # Check access
    if not api_key_access:
        # Permission
        if user_permission & matched_route.permission != matched_route.permission:
            data_out.status = ConnectStatus.UNAUTHORIZED
            data_out.message = "Permission denied"
            return log_and_prepare(
                log_data=log_data,
                data_out=data_out,
                user_data=user_data,
                status_code=status.HTTP_403_FORBIDDEN,
            )

    # Prepare service call
    service_in = ConnectServiceIn(
        apiKey=get_api_key(),
        debug=debug,
        userData=user_data,
        payload=body.payload,
    )
    # Call service
    response = None
    status_code = None
    try:
        response = requests.request(
            method=request.method,
            url=f"http://{matched_service.ip}:{matched_service.listeningPort}/{body.path}",
            json=service_in.model_dump(),
            timeout=10,
            headers={
                "Content-Type": "application/json",
                "User-Agent": f"Connect/{CONNECT_VERSION}",
            },
        )
        status_code = response.status_code
    except Exception as e:
        data_out.status = ConnectStatus.UNREACHABLE
        data_out.message = f"Service did not respond ({e})"
        return log_and_prepare(
            log_data=log_data,
            data_out=data_out,
            user_data=user_data,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    # Process service response
    try:
        response = response.json()
        ConnectServiceOut.model_validate(response)
    except ValidationError:
        data_out.status = ConnectStatus.CONNECT_ERROR
        data_out.message = f"Service response unprocessable ({response})"
        return log_and_prepare(
            log_data=log_data,
            data_out=data_out,
            user_data=user_data,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    except requests.JSONDecodeError:
        data_out.status = ConnectStatus.CONNECT_ERROR
        data_out.message = f"Service response not JSON ({response.text})"
        return log_and_prepare(
            log_data=log_data,
            data_out=data_out,
            user_data=user_data,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    service_out = ConnectServiceOut(
        success=response["success"],
        message=response["message"],
        payload=response["payload"],
    )
    # Prepare response
    data_out.success = service_out.success
    data_out.status = (
        ConnectStatus.ERROR if not data_out.success else ConnectStatus.SUCCESS
    )
    data_out.message = service_out.message
    data_out.payload = service_out.payload

    return log_and_prepare(
        log_data=log_data,
        data_out=data_out,
        user_data=user_data,
        status_code=status_code,
    )

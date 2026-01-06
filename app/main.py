import os
from time import time

from dotenv import load_dotenv
from fastapi import FastAPI, Request, status

from app.models.connect_body import (
    ConnectClientIn,
    ConnectClientOut,
    ConnectServiceIn,
    ConnectServiceOut,
    ConnectStatus,
    UserData,
)
from app.models.register_body import RegisterBodyIn, RegisterBodyOut, RegisterBodyStored
from app.security.key import get_api_key, validate_api_key

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


@api.api_route(
    "/connect",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD", "TRACE"],
)
def connect(body: ConnectClientIn):
    # Timestamp in
    timestamp_in = time() * 1000

    debug = body.debug

    data_out: ConnectClientOut = ConnectClientOut(
        success=False,
        id="",
        status=ConnectStatus.SUCCESS,
        message="",
        payload={},
    )

    # Check JWT validity
    # TODO
    user_data: UserData = {
        "userId": "",
        "permission": 0,
    }
    user_permission = user_data["permission"]

    # Check API key
    api_key_access, _ = validate_api_key(body.apiKey)

    # Check access
    if not api_key_access:
        # Service
        matched_service = None
        for service in registered_services:
            if service.name == body.serviceName:
                matched_service = service
                break
        if matched_service is None:
            data_out.status = ConnectStatus.UNREGISTERED
            data_out.message = "Service not registered"
            return data_out

        # Path/Route
        clean_path = body.path.split("?")[0]
        matched_route = None
        for route in matched_service.routes:
            if route.path == clean_path:
                matched_route = route
                break
        if matched_route is None:
            data_out.status = ConnectStatus.UNREGISTERED
            data_out.message = "Path not in service"
            return data_out

        # Permission
        if user_permission & matched_route.permission != matched_route.permission:
            data_out.status = ConnectStatus.UNAUTHORIZED
            data_out.message = "Permission denied"
            return data_out

    # Prepare service call
    service_in = ConnectServiceIn(
        apiKey=get_api_key(),
        debug=debug,
        userData=user_data,
        payload=body.payload,
    )
    # Call service
    # TODO
    # Process service response
    # TODO
    service_out = ConnectServiceOut(
        success=True,
        message="",
        payload={},
    )
    # Prepare response
    data_out.success = service_out.success
    data_out.status = (
        service_out.status if not service_out.success else ConnectStatus.SUCCESS
    )
    data_out.message = service_out.message
    data_out.payload = service_out.payload

    # Timestamp out
    timestamp_out = time() * 1000

    # Prepare log

    # Log data

    return data_out

from enum import Enum
from typing import Any

from pydantic import BaseModel


class UserData(BaseModel):
    exp: int
    userId: str
    permission: int


class ConnectClientIn(BaseModel):
    apiKey: str | None = None
    clientName: str
    clientVersion: str
    serviceName: str
    path: str
    debug: bool
    payload: Any


class ConnectServiceIn(BaseModel):
    apiKey: str
    debug: bool
    userData: UserData | dict
    payload: Any


class ConnectServiceOut(BaseModel):
    success: bool
    message: str
    payload: Any


class ConnectStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"  # Service error
    UNREGISTERED = "unregistered"  # Service or path does not exist
    UNREACHABLE = "unreachable"  # The service is not responding
    UNAUTHORIZED = "unauthorized"  # Permission denied
    CONNECT_ERROR = "connect_error"  # Connect internal error


class ConnectClientOut(BaseModel):
    success: bool
    id: int
    status: ConnectStatus
    message: str
    payload: Any

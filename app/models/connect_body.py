from enum import Enum

from pydantic import BaseModel


class UserData(BaseModel):
    userId: str
    permission: int


class ConnectClientIn(BaseModel):
    apiKey: str
    clientName: str
    clientVersion: str
    serviceName: str
    path: str
    debug: bool
    payload: dict


class ConnectServiceIn(BaseModel):
    apiKey: str
    debug: bool
    userData: UserData
    payload: dict


class ConnectServiceOut(BaseModel):
    success: bool
    message: str
    payload: dict


class ConnectStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"  # Service error
    UNREGISTERED = "unregistered"  # Service or path does not exist
    UNREACHABLE = "unreachable"  # The service is not responding
    UNAUTHORIZED = "unauthorized"  # Permission denied
    CONNECT = "connect"  # Connect internal error


class ConnectClientOut(BaseModel):
    success: bool
    id: str
    status: ConnectStatus
    message: str
    payload: dict

from pydantic import BaseModel

from app.models.connect_body import ConnectStatus, UserData
from app.models.register_body import HttpMethod


class Identification(BaseModel):
    connectVersion: str
    clientName: str
    clientVersion: str
    serviceName: str
    serviceVersion: str


class Request(BaseModel):
    success: bool
    path: str
    method: HttpMethod
    httpCode: int
    status: ConnectStatus
    message: str


class Data(BaseModel):
    debug: bool
    userData: UserData | dict
    payloadIn: dict
    payloadOut: dict


class ConnectLog(BaseModel):
    id: int
    timestampIn: float
    timestampOut: float
    identification: Identification
    request: Request
    data: Data

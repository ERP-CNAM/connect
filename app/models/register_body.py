from enum import Enum
from typing import Optional

from pydantic import BaseModel


class HttpMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    OPTIONS = "OPTIONS"
    HEAD = "HEAD"
    TRACE = "TRACE"


class Route(BaseModel):
    path: str
    method: HttpMethod
    permission: int


class RegisterBodyOut(BaseModel):
    name: str
    description: str
    version: str
    routes: list[Route]


class RegisterBodyIn(RegisterBodyOut):
    overrideIp: str | None = None
    listeningPort: int
    apiKey: str


class RegisterBodyStored(RegisterBodyOut):
    listeningPort: int
    ip: str

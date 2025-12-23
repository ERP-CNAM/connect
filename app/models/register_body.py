from enum import Enum

from pydantic import BaseModel


class HttpMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    OPTIONS = "OPTIONS"
    HEAD = "HEAD"
    TRACe = "TRACE"


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
    listeningPort: int
    apiKey: str


class RegisterBodyStored(RegisterBodyOut):
    listeningPort: int
    ip: str

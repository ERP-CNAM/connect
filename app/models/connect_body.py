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


class ConnectClientOut(BaseModel):
    success: bool
    id: str
    status: str
    message: str
    payload: dict

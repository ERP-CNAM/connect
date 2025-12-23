from fastapi import FastAPI, Response, status

from app.models.register_body import RegisterBody

api = FastAPI()
registered_services: list[RegisterBody] = list()


@api.get("/")
def read_root():
    return {"Hello": "World"}


@api.get("/ping", status_code=status.HTTP_200_OK)
def ping():
    return {}


@api.post("/register")
def register(body: RegisterBody, response: Response):
    valid_key = True  # TODO: implement api key mechanism
    if valid_key:
        registered_services.append(body)
        response.status_code = status.HTTP_200_OK
    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED
    return {}

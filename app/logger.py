import logging
import os
from logging.handlers import RotatingFileHandler
from time import time

from dotenv import load_dotenv
from fastapi.responses import JSONResponse

from app.models.connect_body import ConnectClientOut, UserData
from app.models.connect_log import ConnectLog, FixedLogData

load_dotenv(dotenv_path=".env")

CONNECT_VERSION = os.getenv("CONNECT_VERSION")
assert CONNECT_VERSION is not None, "CONNECT_VERSION environment variable is not set"

logger = logging.getLogger("HTTP Requests")
logger.setLevel(logging.DEBUG)

log_file = os.path.join(os.path.curdir, "logs", "connect.log")

file_handler = RotatingFileHandler(log_file, mode="a", maxBytes=4000000, backupCount=10)
file_handler.setLevel(logging.DEBUG)

logger.addHandler(file_handler)


def log_and_prepare(
    log_data: FixedLogData,
    data_out: ConnectClientOut,
    user_data: UserData | dict,
    status_code: int,
) -> JSONResponse:
    # Timestamp out
    timestamp_out = time() * 1000

    # Prepare log
    log_id = "0"
    log = ConnectLog(
        id=log_id,
        timestampIn=log_data.timestamp_in,
        timestampOut=timestamp_out,
        identification={
            "connectVersion": CONNECT_VERSION,
            "clientName": log_data.body.clientName,
            "clientVersion": log_data.body.clientVersion,
            "serviceName": log_data.body.serviceName,
            "serviceVersion": log_data.service_version,
        },
        request={
            "success": data_out.success,
            "path": log_data.body.path,
            "method": log_data.method,
            "httpCode": status_code,
            "status": data_out.status,
            "message": data_out.message,
        },
        data={
            "debug": log_data.body.debug,
            "userData": user_data,
            "payloadIn": log_data.body.payload,
            "payloadOut": data_out.payload,
        },
    )

    # Log data
    # TODO
    print(log.model_dump_json())
    logger.info(log.model_dump_json())

    # Update response
    data_out.id = log_id

    return JSONResponse(status_code=status_code, content=data_out.model_dump())

import contextlib
from typing import Any

from fastapi import HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


async def validation_exception_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
    """Exception handler to handle Request validation errors
    Args:
        request (Request): Request object
        exc (RequestValidationError): Exception object

    Returns:
        JSONResponse: Returns error data in the desired format
    """

    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=get_error_response('Request validation error', status.HTTP_422_UNPROCESSABLE_ENTITY, exc.errors()))


async def http_exception_handler(_request: Request, exc: HTTPException) -> JSONResponse:
    """Exception handler to handle exception of type HTTPException
    Args:
        request (Request): Request object
        exc (HTTPException): Exception object

    Returns:
        JSONResponse: Returns error data in the desired format
    """
    code = exc.status_code or status.HTTP_404_NOT_FOUND
    headers = {}
    with contextlib.suppress(AttributeError):
        headers = exc.headers
    return JSONResponse(status_code=code, content=get_error_response(exc.detail, code), headers=headers)


def get_error_response(message: str, code: int, detail: Any = None) -> dict[str, Any]:
    """Function to format error data

    Args:
        message (str): Error message
        code (int): Error code

    Returns:
        JSON: Returns error data in the desired format
    """
    error = {'status': 'FAIL', 'errorData': {'errorCode': code, 'message': message}}
    if detail:
        error['errorData'].update({'detail': detail})
    return jsonable_encoder(error)

"""Normalised API error responses."""
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler as drf_exception_handler


class A2ZAPIException(APIException):
    """Base exception with machine-readable error code."""

    default_code = "ERROR"

    def __init__(self, detail=None, code=None, status_code=None):
        if status_code is not None:
            self.status_code = status_code
        if code is not None:
            self.default_code = code
        super().__init__(detail=detail, code=code or self.default_code)


class ValidationError(A2ZAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "VALIDATION_ERROR"


class NotFoundError(A2ZAPIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_code = "NOT_FOUND"


class ConflictError(A2ZAPIException):
    status_code = status.HTTP_409_CONFLICT
    default_code = "CONFLICT"


class BusinessRuleError(A2ZAPIException):
    status_code = 422
    default_code = "BUSINESS_RULE_VIOLATION"


def _first_field_error_message(details: dict) -> str:
    for value in details.values():
        if isinstance(value, list) and value:
            return str(value[0])
        if isinstance(value, str):
            return value
    return "Validation failed."


def a2z_exception_handler(exc, context):
    response = drf_exception_handler(exc, context)
    if response is None:
        return response

    error_code = getattr(exc, "default_code", "ERROR")
    if hasattr(exc, "get_codes"):
        codes = exc.get_codes()
        if isinstance(codes, str):
            error_code = codes.upper()

    details = response.data
    if isinstance(details, dict):
        if "detail" in details:
            message = str(details["detail"])
            field_details = {k: v for k, v in details.items() if k != "detail"}
            details = field_details or None
        else:
            message = _first_field_error_message(details)
    elif isinstance(details, list):
        message = "; ".join(str(item) for item in details)
        details = None
    else:
        message = str(details)
        details = None

    response.data = {
        "error": {
            "code": error_code,
            "message": message,
            "details": details,
        }
    }
    return response

from fastapi import status

# Standard, stable error codes clients can branch on (never change these strings once shipped).
BAD_REQUEST = "BAD_REQUEST"
UNAUTHORIZED = "UNAUTHORIZED"
FORBIDDEN = "FORBIDDEN"
NOT_FOUND = "NOT_FOUND"
CONFLICT = "CONFLICT"
VALIDATION_ERROR = "VALIDATION_ERROR"
INVALID_REFERENCE = "INVALID_REFERENCE"
INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"

_STATUS_TO_CODE = {
    status.HTTP_400_BAD_REQUEST: BAD_REQUEST,
    status.HTTP_401_UNAUTHORIZED: UNAUTHORIZED,
    status.HTTP_403_FORBIDDEN: FORBIDDEN,
    status.HTTP_404_NOT_FOUND: NOT_FOUND,
    status.HTTP_409_CONFLICT: CONFLICT,
    status.HTTP_422_UNPROCESSABLE_ENTITY: VALIDATION_ERROR,
    status.HTTP_500_INTERNAL_SERVER_ERROR: INTERNAL_SERVER_ERROR,
}


def code_for_status(status_code: int) -> str:
    return _STATUS_TO_CODE.get(status_code, "ERROR")


class AppError(Exception):
    """Raise inside endpoints/CRUD to produce a consistent envelope with a specific HTTP status."""

    def __init__(self, *, status_code: int, code: str, message: str):
        self.status_code = status_code
        self.code = code
        self.message = message
        super().__init__(message)

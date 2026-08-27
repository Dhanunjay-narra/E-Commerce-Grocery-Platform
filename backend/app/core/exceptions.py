"""Standardized typed application exceptions and HTTP response handlers."""
from typing import Any, Dict, Optional
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


class AppException(Exception):
    """Base application exception."""
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code: str = "INTERNAL_SERVER_ERROR"
    message: str = "An unexpected server error occurred."

    def __init__(
        self,
        message: Optional[str] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        if message:
            self.message = message
        if error_code:
            self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class EntityNotFoundError(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    error_code = "ENTITY_NOT_FOUND"
    message = "The requested resource was not found."


class AuthenticationError(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = "AUTHENTICATION_FAILED"
    message = "Authentication credentials were not provided or are invalid."


class PermissionDeniedError(AppException):
    status_code = status.HTTP_403_FORBIDDEN
    error_code = "PERMISSION_DENIED"
    message = "You do not have permission to perform this action."


class ValidationError(AppException):
    status_code = 422
    error_code = "VALIDATION_FAILED"
    message = "Provided input data is invalid."


class ConflictError(AppException):
    status_code = status.HTTP_409_CONFLICT
    error_code = "RESOURCE_CONFLICT"
    message = "Resource already exists or conflicts with current state."


class InsufficientInventoryError(AppException):
    status_code = status.HTTP_409_CONFLICT
    error_code = "INSUFFICIENT_INVENTORY"
    message = "One or more items in the order do not have sufficient stock available."


class InvalidStateTransitionError(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "INVALID_STATE_TRANSITION"
    message = "The requested status transition is not allowed for this entity."


class PaymentError(AppException):
    status_code = status.HTTP_402_PAYMENT_REQUIRED
    error_code = "PAYMENT_FAILED"
    message = "Payment authorization or capture failed."


class DeliverySlotUnavailableError(AppException):
    status_code = status.HTTP_409_CONFLICT
    error_code = "DELIVERY_SLOT_UNAVAILABLE"
    message = "The selected delivery slot is full or unavailable for your zone."


def register_exception_handlers(app: FastAPI) -> None:
    """Registers unified JSON exception handlers on the FastAPI application."""

    @app.exception_handler(AppException)
    async def handle_app_exception(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": exc.error_code,
                    "message": exc.message,
                    "details": exc.details,
                },
            },
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "error": {
                    "code": "REQUEST_VALIDATION_ERROR",
                    "message": "Invalid request parameters or payload.",
                    "details": {"errors": exc.errors()},
                },
            },
        )

    @app.exception_handler(Exception)
    async def handle_general_exception(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": str(exc) if app.debug else "An unexpected internal server error occurred.",
                    "details": {},
                },
            },
        )

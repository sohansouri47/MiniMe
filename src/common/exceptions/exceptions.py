from http import HTTPStatus


class AppException(Exception):
    def __init__(
        self,
        message: str,
        *,
        status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR,
        code: str = "internal_error",
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code


class NotFoundException(AppException):
    def __init__(self, message: str) -> None:
        super().__init__(
            message,
            status_code=HTTPStatus.NOT_FOUND,
            code="not_found",
        )


class ValidationException(AppException):
    def __init__(self, message: str) -> None:
        super().__init__(
            message,
            status_code=HTTPStatus.BAD_REQUEST,
            code="validation_error",
        )


class ProviderConfigurationException(AppException):
    def __init__(self, message: str) -> None:
        super().__init__(
            message,
            status_code=HTTPStatus.SERVICE_UNAVAILABLE,
            code="provider_configuration_error",
        )


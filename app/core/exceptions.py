from fastapi import status


class AppError(Exception):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "Internal server error"

    def __init__(self, detail: str | None = None):
        self.detail = detail or self.default_detail
        super().__init__(self.detail)


class BadRequestError(AppError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Bad request"


class NotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Resource not found"


class ConflictError(AppError):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Conflict"


class ExternalServiceError(AppError):
    status_code = status.HTTP_502_BAD_GATEWAY
    default_detail = "External service failure"


class MinioError(ExternalServiceError):
    default_detail = "MinIO service error"

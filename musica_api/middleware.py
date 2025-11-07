"""
Middleware de logging para la API de Música.
Registra solicitudes HTTP, errores y métricas de rendimiento.
Desarrollado por Isabella Ramírez Franco (@codebell-alt)
"""

import time
import uuid
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from musica_api.logging_config import get_logger

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware para logging automático de requests y responses.
    """

    def __init__(self, app, log_requests: bool = True, log_responses: bool = True):
        super().__init__(app)
        self.log_requests = log_requests
        self.log_responses = log_responses

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Procesa cada request y response, registrando información relevante.
        """
        # Generar ID único para la request
        request_id = str(uuid.uuid4())[:8]

        # Agregar el request_id al contexto
        request.state.request_id = request_id

        # Tiempo de inicio
        start_time = time.time()

        # Log de request entrante
        if self.log_requests:
            await self._log_request(request, request_id)

        # Procesar request
        try:
            response = await call_next(request)

            # Calcular tiempo de procesamiento
            process_time = time.time() - start_time

            # Log de response
            if self.log_responses:
                await self._log_response(request, response, request_id, process_time)

            # Agregar headers de logging
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(round(process_time, 3))

            return response

        except Exception as exc:
            # Log de error
            process_time = time.time() - start_time
            await self._log_error(request, exc, request_id, process_time)

            # Retornar error en formato JSON
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Error interno del servidor",
                    "request_id": request_id,
                    "error_type": type(exc).__name__,
                },
                headers={
                    "X-Request-ID": request_id,
                    "X-Process-Time": str(round(process_time, 3)),
                },
            )

    async def _log_request(self, request: Request, request_id: str) -> None:
        """Log información del request entrante."""
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "Unknown")

        logger.info(
            f"[{request_id}] {request.method} {request.url.path} "
            f"- IP: {client_ip} - User-Agent: {user_agent}"
        )

        # Log query parameters si existen
        if request.query_params:
            logger.debug(f"[{request_id}] Query params: {dict(request.query_params)}")

    async def _log_response(
        self, request: Request, response: Response, request_id: str, process_time: float
    ) -> None:
        """Log información del response."""
        status_color = self._get_status_color(response.status_code)

        logger.info(
            f"[{request_id}] {request.method} {request.url.path} "
            f"- Status: {status_color}{response.status_code}\033[0m "
            f"- Time: {process_time:.3f}s"
        )

        # Log adicional para errores
        if response.status_code >= 400:
            logger.warning(
                f"[{request_id}] Error response - Status: {response.status_code} "
                f"- Path: {request.url.path}"
            )

    async def _log_error(
        self, request: Request, exc: Exception, request_id: str, process_time: float
    ) -> None:
        """Log información de errores."""
        logger.error(
            f"[{request_id}] ERROR {request.method} {request.url.path} "
            f"- Exception: {type(exc).__name__}: {str(exc)} "
            f"- Time: {process_time:.3f}s",
            exc_info=True,
        )

    def _get_client_ip(self, request: Request) -> str:
        """Obtener IP del cliente considerando proxies."""
        # Revisar headers de proxy
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        # IP directa
        if hasattr(request.client, "host"):
            return request.client.host

        return "unknown"

    def _get_status_color(self, status_code: int) -> str:
        """Obtener color ANSI basado en status code."""
        if status_code < 300:
            return "\033[92m"  # Verde
        elif status_code < 400:
            return "\033[93m"  # Amarillo
        elif status_code < 500:
            return "\033[91m"  # Rojo claro
        else:
            return "\033[95m"  # Magenta


class APIMetricsLogger:
    """
    Logger especializado para métricas de la API.
    """

    def __init__(self):
        self.logger = get_logger(f"{__name__}.metrics")
        self.request_count = 0
        self.error_count = 0

    def log_endpoint_access(
        self, endpoint: str, method: str, user_id: int | None = None
    ):
        """Log acceso a endpoints específicos."""
        self.request_count += 1
        self.logger.info(
            f"Endpoint accessed: {method} {endpoint} "
            f"- User: {user_id or 'anonymous'} "
            f"- Total requests: {self.request_count}"
        )

    def log_database_operation(self, operation: str, table: str, duration: float):
        """Log operaciones de base de datos."""
        self.logger.debug(
            f"DB Operation: {operation} on {table} - Duration: {duration:.3f}s"
        )

    def log_validation_error(self, field: str, value: str, error: str):
        """Log errores de validación."""
        self.logger.warning(
            f"Validation error - Field: {field}, Value: {value}, Error: {error}"
        )

    def log_business_logic_error(self, operation: str, error: str, context: dict):
        """Log errores de lógica de negocio."""
        self.error_count += 1
        self.logger.error(
            f"Business logic error - Operation: {operation}, Error: {error}, "
            f"Context: {context}, Total errors: {self.error_count}"
        )


# Instancia global para métricas
metrics_logger = APIMetricsLogger()


def log_endpoint_access(endpoint: str, method: str, user_id: int | None = None):
    """Función helper para logging de acceso a endpoints."""
    metrics_logger.log_endpoint_access(endpoint, method, user_id)


def log_database_operation(operation: str, table: str, duration: float):
    """Función helper para logging de operaciones DB."""
    metrics_logger.log_database_operation(operation, table, duration)


def log_validation_error(field: str, value: str, error: str):
    """Función helper para logging de errores de validación."""
    metrics_logger.log_validation_error(field, value, error)


def log_business_error(operation: str, error: str, **context):
    """Función helper para logging de errores de negocio."""
    metrics_logger.log_business_logic_error(operation, error, context)

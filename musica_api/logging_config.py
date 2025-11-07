"""
Sistema de logging configurado para la API de Música.
Proporciona configuración de logging para desarrollo y producción.
Desarrollado por Isabella Ramírez Franco (@codebell-alt)
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Any

from pydantic_settings import BaseSettings


class LoggingSettings(BaseSettings):
    """Configuración de logging desde variables de entorno."""

    log_level: str = "INFO"
    log_to_file: bool = True
    log_file_path: str = "logs/musica_api.log"
    log_max_bytes: int = 10 * 1024 * 1024  # 10MB
    log_backup_count: int = 5
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_date_format: str = "%Y-%m-%d %H:%M:%S"

    class Config:
        env_prefix = "MUSICA_API_"


def setup_logging(settings: LoggingSettings | None = None) -> dict[str, Any]:
    """
    Configura el sistema de logging para la aplicación.

    Args:
        settings: Configuración de logging. Si es None, usa valores por defecto.

    Returns:
        Diccionario con la configuración de logging aplicada.
    """
    if settings is None:
        settings = LoggingSettings()

    # Crear directorio de logs si no existe
    if settings.log_to_file:
        log_path = Path(settings.log_file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)

    # Configurar nivel de logging
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # Crear formatter
    formatter = logging.Formatter(
        fmt=settings.log_format, datefmt=settings.log_date_format
    )

    # Configurar root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Limpiar handlers existentes
    root_logger.handlers.clear()

    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Handler para archivo (con rotación)
    if settings.log_to_file:
        file_handler = logging.handlers.RotatingFileHandler(
            filename=settings.log_file_path,
            maxBytes=settings.log_max_bytes,
            backupCount=settings.log_backup_count,
            encoding="utf-8",
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Configurar loggers específicos
    configure_uvicorn_logging(log_level)
    configure_sqlalchemy_logging(log_level)

    # Logger específico para la API
    api_logger = logging.getLogger("musica_api")
    api_logger.setLevel(log_level)

    logging.info(
        f"Sistema de logging configurado - Nivel: {settings.log_level}, "
        f"Archivo: {settings.log_to_file}"
    )

    return {
        "level": settings.log_level,
        "log_to_file": settings.log_to_file,
        "log_file": settings.log_file_path if settings.log_to_file else None,
        "handlers": len(root_logger.handlers),
    }


def configure_uvicorn_logging(log_level: int) -> None:
    """Configurar logging de Uvicorn."""
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.setLevel(log_level)

    uvicorn_access_logger = logging.getLogger("uvicorn.access")
    uvicorn_access_logger.setLevel(log_level)


def configure_sqlalchemy_logging(log_level: int) -> None:
    """Configurar logging de SQLAlchemy."""
    # Reducir verbosidad de SQLAlchemy en desarrollo
    if log_level <= logging.DEBUG:
        sqlalchemy_logger = logging.getLogger("sqlalchemy.engine")
        sqlalchemy_logger.setLevel(logging.INFO)
    else:
        sqlalchemy_logger = logging.getLogger("sqlalchemy")
        sqlalchemy_logger.setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Obtener un logger configurado para un módulo específico.

    Args:
        name: Nombre del logger (generalmente __name__)

    Returns:
        Logger configurado
    """
    return logging.getLogger(name)


class LoggerMixin:
    """
    Mixin para agregar capacidades de logging a clases.
    """

    @property
    def logger(self) -> logging.Logger:
        """Obtener logger para la clase actual."""
        return get_logger(f"{self.__class__.__module__}.{self.__class__.__name__}")


# Configuración predeterminada para desarrollo
def setup_development_logging() -> None:
    """Configuración rápida para desarrollo."""
    settings = LoggingSettings(
        log_level="DEBUG",
        log_to_file=True,
        log_file_path="logs/dev_musica_api.log",
    )
    setup_logging(settings)


# Configuración para producción
def setup_production_logging() -> None:
    """Configuración para producción."""
    settings = LoggingSettings(
        log_level="INFO",
        log_to_file=True,
        log_file_path="/var/log/musica_api/musica_api.log",
    )
    setup_logging(settings)

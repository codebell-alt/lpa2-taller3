"""
Configuración de la aplicación.
Maneja diferentes entornos: desarrollo, pruebas y producción.
Configurado por Isabella Ramírez Franco (@isabellaramirez)
"""

from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Configuración de la aplicación usando Pydantic Settings.
    Lee las variables de entorno desde el archivo .env
    """

    # Configuración básica de la aplicación
    app_name: str = "API de Música"
    app_version: str = "1.0.0"
    app_description: str = "API RESTful para gestionar usuarios, canciones y favoritos"

    # Información del desarrollador
    developer_name: str = "Isabella Ramírez Franco"
    developer_github: str = "@codebell-alt"
    developer_email: str = "isabella315784@gmail.com"
    developer_program: str = "Ingeniería en Sistemas"
    developer_semester: str = "Sexto"

    # Configuración del entorno
    environment: Literal["development", "testing", "production"] = "development"

    # Configuración de la base de datos
    database_url: str = "sqlite:///./musica.db"

    # Configuración del servidor (Puerto 8001 como especificado)
    host: str = "127.0.0.1"
    port: int = 8001
    debug: bool = True

    # Configuración de CORS
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8001",
    ]

    # Configuración de logging
    log_level: str = "INFO"

    # Configuración de seguridad (para futuras mejoras)
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    class Config:
        """
        Configuración de Pydantic Settings.
        """

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

        # Validación personalizada para database_url
        @field_validator("database_url")
        def validate_database_url(cls, v):
            if not v:
                raise ValueError("DATABASE_URL no puede estar vacío")
            return v

        #     return v


# Crear una instancia global de Settings
settings = Settings()


# Crear diferentes configuraciones para cada entorno
class DevelopmentSettings(Settings):
    """Configuración para el entorno de desarrollo."""

    debug: bool = True
    # TODO: Agregar configuraciones específicas de desarrollo


class TestingSettings(Settings):
    """Configuración para el entorno de pruebas."""

    # Usar una base de datos diferente para pruebas
    database_url: str = "sqlite:///./test_musica.db"
    # TODO: Agregar configuraciones específicas de pruebas


class ProductionSettings(Settings):
    """Configuración para el entorno de producción."""

    debug: bool = False
    # TODO: Agregar configuraciones específicas de producción
    # TODO: Cambiar a una base de datos más robusta (PostgreSQL, MySQL)
    # database_url: str = "postgresql://user:password@localhost/musica_prod"


# Función para obtener la configuración según el entorno
def get_settings() -> Settings:
    """
    Retorna la configuración apropiada según el entorno.
    """
    env = settings.environment.lower()

    if env == "testing":
        return TestingSettings()
    elif env == "production":
        return ProductionSettings()
    else:
        return DevelopmentSettings()


# Instancia global de configuración
app_settings = get_settings()


# TODO: Opcional - Agregar validación de configuración al inicio
# def validate_settings():
#     """Valida que todas las configuraciones necesarias estén presentes."""
#     required_settings = ["database_url", "app_name"]
#     for setting in required_settings:
#         if not getattr(settings, setting, None):
#             raise ValueError(f"Configuración requerida no encontrada: {setting}")

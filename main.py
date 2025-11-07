"""
API de Música - Aplicación principal
Desarrollada con FastAPI, SQLModel y Pydantic
Creado por Isabella Ramírez Franco (@isabellaramirez)
"""

import logging
import time
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from musica_api.config import settings

# Imports del proyecto
from musica_api.database import (
    create_db_and_tables,
    obtener_estadisticas_db,
    verificar_conexion_db,
)
from musica_api.routers import canciones, favoritos, usuarios

# Routers importados y listos para usar

# Configuración de logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"{settings.app_name.lower()}.log"),
    ],
)
logger = logging.getLogger(__name__)

# Variable global para tiempo de inicio
start_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestor de ciclo de vida de la aplicación.
    Se ejecuta al iniciar y al cerrar la aplicación.
    """
    # Startup: Crear tablas en la base de datos
    logger.info("Iniciando API de Música...")
    logger.info(f"Desarrollado por {settings.developer_name}")
    logger.info(f"GitHub: {settings.developer_github}")

    try:
        create_db_and_tables()
        logger.info("Base de datos inicializada correctamente")
    except Exception as e:
        logger.error(f"Error al inicializar la base de datos: {e}")
        raise

    yield

    # Shutdown: Limpiar recursos si es necesario
    logger.info("Cerrando aplicación...")
    logger.info("Hasta luego! - Isabella Ramírez Franco")


# Crear la instancia de FastAPI con metadatos completos
app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    lifespan=lifespan,
    contact={
        "name": "Isabella Ramírez Franco",
        "email": "isabella315784@gmail.com",
        "url": "https://github.com/codebell-alt",
    },
    license_info={"name": "MIT License", "url": "https://opensource.org/licenses/MIT"},
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configurar CORS con configuraciones del archivo .env
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)


# Middleware para logging de requests
@app.middleware("http")
async def log_requests(request, call_next):
    """Middleware para registrar todas las peticiones HTTP"""
    start_time = time.time()

    # Procesar la request
    response = await call_next(request)

    # Calcular tiempo de procesamiento
    process_time = time.time() - start_time

    # Log de la request
    logger.info(
        f"{request.method} {request.url} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.4f}s"
    )

    # Agregar header con tiempo de procesamiento
    response.headers["X-Process-Time"] = str(process_time)

    return response


# Montar archivos estáticos para el frontend
try:
    # Montar archivos CSS, JS e imágenes
    app.mount("/static", StaticFiles(directory="frontend"), name="static")
    logger.info("Archivos estáticos montados en /static")
except Exception as e:
    logger.warning(f"No se pudieron montar archivos estáticos: {e}")

# Incluir los routers de la API
app.include_router(usuarios.router)
app.include_router(canciones.router)
app.include_router(favoritos.router)

# ============================================================================
# ENDPOINTS PRINCIPALES
# ============================================================================


@app.get("/", tags=["Frontend"])
async def frontend():
    """
    Sirve el frontend de la aplicación.
    Retorna el archivo index.html con la interfaz de usuario.
    """
    return FileResponse("frontend/index.html")


@app.get("/api", tags=["Root"])
async def root():
    """
    Endpoint de información de la API.
    Retorna información básica y enlaces a la documentación.
    """
    uptime = time.time() - start_time
    uptime_formatted = (
        f"{uptime // 3600:.0f}h {(uptime % 3600) // 60:.0f}m {uptime % 60:.0f}s"
    )

    return {
        "mensaje": f"Bienvenido a {settings.app_name}",
        "descripcion": settings.app_description,
        "version": settings.app_version,
        "desarrollador": {
            "nombre": "Isabella Ramírez Franco",
            "github": "@codebell-alt",
            "email": "isabella315784@gmail.com",
        },
        "documentacion": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_json": "/openapi.json",
        },
        "endpoints_principales": {
            "usuarios": "/api/usuarios",
            "canciones": "/api/canciones",
            "favoritos": "/api/favoritos",
            "health": "/health",
            "stats": "/stats",
        },
        "uptime": uptime_formatted,
        "puerto": settings.port,
        "estado": "Activo",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint para verificar el estado de la API.
    Útil para sistemas de monitoreo y orquestación.
    """
    # Verificar conexión a la base de datos
    db_status = verificar_conexion_db()

    # Calcular uptime
    uptime = time.time() - start_time

    return {
        "status": "healthy" if db_status else "unhealthy",
        "timestamp": time.time(),
        "uptime_seconds": uptime,
        "database": "connected" if db_status else "disconnected",
        "version": settings.app_version,
        "environment": settings.environment,
        "port": settings.port,
        "developer": "Isabella Ramírez Franco",
    }


@app.get("/stats", tags=["Estadísticas"])
async def estadisticas():
    """
    Endpoint para obtener estadísticas de la base de datos.
    """
    try:
        stats = obtener_estadisticas_db()
        return {
            "exito": True,
            "estadisticas": stats,
            "api_info": {
                "nombre": settings.app_name,
                "version": settings.app_version,
                "desarrollador": "Isabella Ramírez Franco",
            },
        }
    except Exception as e:
        logger.error(f"Error al obtener estadísticas: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error al obtener estadísticas: {str(e)}"
        )


@app.get("/info/desarrollador", tags=["Información"])
async def info_desarrollador():
    """
    Endpoint con información del desarrollador.
    """
    return {
        "desarrollador": {
            "nombre_completo": "Isabella Ramírez Franco",
            "github": "@codebell-alt",
            "email": "isabella315784@gmail.com",
        },
        "proyecto": {
            "nombre": settings.app_name,
            "descripcion": settings.app_description,
            "version": settings.app_version,
            "repositorio": "https://github.com/codebell-alt/lpa2-taller3",
        },
        "tecnologias": [
            "FastAPI",
            "SQLModel",
            "Pydantic",
            "SQLite",
            "TailwindCSS",
            "Python 3.12+",
        ],
    }


# ============================================================================
# MANEJADORES DE ERRORES PERSONALIZADOS
# ============================================================================


@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Manejador personalizado para errores 404"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Recurso no encontrado",
            "mensaje": "La URL solicitada no existe en esta API",
            "sugerencia": "Revisa la documentación en /docs",
            "desarrollador": "Isabella Ramírez Franco",
        },
    )


@app.exception_handler(500)
async def internal_server_error_handler(request, exc):
    """Manejador personalizado para errores 500"""
    logger.error(f"Error interno del servidor: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Error interno del servidor",
            "mensaje": "Ocurrió un error inesperado. Por favor, intenta de nuevo.",
            "contacto": "isabella315784@gmail.com",
            "desarrollador": "Isabella Ramírez Franco",
        },
    )


# ============================================================================
# PUNTO DE ENTRADA PRINCIPAL
# ============================================================================

if __name__ == "__main__":
    logger.info(f"Iniciando {settings.app_name}")
    logger.info("Desarrollado por Isabella Ramírez Franco")
    logger.info(f"Servidor: http://{settings.host}:{settings.port}")

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )

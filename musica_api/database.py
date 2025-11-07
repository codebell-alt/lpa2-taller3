"""
Configuración de la base de datos para la API de Música.
Maneja la conexión a SQLite y la creación de tablas.
Creado por Isabella Ramírez Franco (@isabellaramirez)
"""

import logging
from collections.abc import Generator
from datetime import datetime

from sqlmodel import Session, SQLModel, create_engine, select

from musica_api.config import app_settings
from musica_api.models import Cancion, Favorito, Usuario

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear el motor de la base de datos
engine = create_engine(
    app_settings.database_url,
    connect_args={"check_same_thread": False}
    if "sqlite" in app_settings.database_url
    else {},
    echo=app_settings.debug,  # Mostrar las consultas SQL en modo debug
)


def create_db_and_tables():
    """
    Crear la base de datos y todas las tablas necesarias.
    Se ejecuta automáticamente al iniciar la aplicación.
    """
    try:
        SQLModel.metadata.create_all(engine)
        logger.info("Base de datos y tablas creadas exitosamente")

        # Verificar si ya hay datos, si no, crear datos iniciales
        with Session(engine) as session:
            usuarios_count = len(session.exec(select(Usuario)).all())
            canciones_count = len(session.exec(select(Cancion)).all())

            if usuarios_count == 0 and canciones_count == 0:
                logger.info("Creando datos iniciales...")
                crear_datos_iniciales()

    except Exception as e:
        logger.error(f"Error al crear la base de datos: {e}")
        raise


def get_session() -> Generator[Session, None, None]:
    """
    Obtener una sesión de base de datos.
    Utiliza el patrón de dependencias de FastAPI.

    Yields:
        Session: Sesión de SQLModel para realizar operaciones en la BD
    """
    with Session(engine) as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Error en la sesión de base de datos: {e}")
            session.rollback()
            raise
        finally:
            session.close()


def crear_datos_iniciales():
    """
    Crear datos iniciales para la aplicación.
    Incluye 5 usuarios y 10 canciones como especificado.
    """
    try:
        with Session(engine) as session:
            # Crear 5 usuarios iniciales
            usuarios_iniciales = [
                Usuario(
                    nombre="Isabella Ramírez Franco", correo="isabella315784@gmail.com"
                ),
                Usuario(nombre="Juan Carlos Pérez", correo="juan.perez@example.com"),
                Usuario(nombre="María García López", correo="maria.garcia@example.com"),
                Usuario(nombre="Carlos Eduardo Ruiz", correo="carlos.ruiz@example.com"),
                Usuario(nombre="Ana Sofía Martínez", correo="ana.martinez@example.com"),
            ]

            # Agregar usuarios a la sesión
            for usuario in usuarios_iniciales:
                session.add(usuario)

            session.commit()
            logger.info("Usuarios iniciales creados")

            # Crear 10 canciones iniciales
            canciones_iniciales = [
                Cancion(
                    titulo="Bohemian Rhapsody",
                    artista="Queen",
                    album="A Night at the Opera",
                    duracion=355,
                    año=1975,
                    genero="Rock",
                ),
                Cancion(
                    titulo="Imagine",
                    artista="John Lennon",
                    album="Imagine",
                    duracion=183,
                    año=1971,
                    genero="Rock",
                ),
                Cancion(
                    titulo="Hotel California",
                    artista="Eagles",
                    album="Hotel California",
                    duracion=391,
                    año=1976,
                    genero="Rock",
                ),
                Cancion(
                    titulo="Billie Jean",
                    artista="Michael Jackson",
                    album="Thriller",
                    duracion=294,
                    año=1982,
                    genero="Pop",
                ),
                Cancion(
                    titulo="Like a Rolling Stone",
                    artista="Bob Dylan",
                    album="Highway 61 Revisited",
                    duracion=370,
                    año=1965,
                    genero="Folk Rock",
                ),
                Cancion(
                    titulo="Smells Like Teen Spirit",
                    artista="Nirvana",
                    album="Nevermind",
                    duracion=301,
                    año=1991,
                    genero="Grunge",
                ),
                Cancion(
                    titulo="What's Going On",
                    artista="Marvin Gaye",
                    album="What's Going On",
                    duracion=233,
                    año=1971,
                    genero="Soul",
                ),
                Cancion(
                    titulo="Stairway to Heaven",
                    artista="Led Zeppelin",
                    album="Led Zeppelin IV",
                    duracion=482,
                    año=1971,
                    genero="Rock",
                ),
                Cancion(
                    titulo="Hey Jude",
                    artista="The Beatles",
                    album="Hey Jude",
                    duracion=431,
                    año=1968,
                    genero="Rock",
                ),
                Cancion(
                    titulo="Purple Haze",
                    artista="Jimi Hendrix",
                    album="Are You Experienced",
                    duracion=170,
                    año=1967,
                    genero="Rock Psicodélico",
                ),
            ]

            # Agregar canciones a la sesión
            for cancion in canciones_iniciales:
                session.add(cancion)

            session.commit()
            logger.info("Canciones iniciales creadas")

            # Crear algunos favoritos de ejemplo
            favoritos_iniciales = [
                Favorito(id_usuario=1, id_cancion=1),  # Isabella - Bohemian Rhapsody
                Favorito(id_usuario=1, id_cancion=2),  # Isabella - Imagine
                Favorito(id_usuario=2, id_cancion=3),  # Juan - Hotel California
                Favorito(id_usuario=2, id_cancion=4),  # Juan - Billie Jean
                Favorito(id_usuario=3, id_cancion=1),  # María - Bohemian Rhapsody
            ]

            for favorito in favoritos_iniciales:
                session.add(favorito)

            session.commit()
            logger.info("Favoritos iniciales creados")
            logger.info("Datos iniciales completados exitosamente")

    except Exception as e:
        logger.error(f"Error al crear datos iniciales: {e}")
        raise


def verificar_conexion_db() -> bool:
    """
    Verificar que la conexión a la base de datos esté funcionando.

    Returns:
        bool: True si la conexión es exitosa, False en caso contrario
    """
    try:
        with Session(engine) as session:
            # Intentar una consulta simple
            session.exec(select(Usuario).limit(1)).first()
            logger.info("Conexión a la base de datos verificada")
            return True
    except Exception as e:
        logger.error(f"Error al verificar conexión a la base de datos: {e}")
        return False


def obtener_estadisticas_db():
    """
    Obtener estadísticas básicas de la base de datos.

    Returns:
        dict: Diccionario con estadísticas de usuarios, canciones y favoritos
    """
    try:
        with Session(engine) as session:
            usuarios_count = len(session.exec(select(Usuario)).all())
            canciones_count = len(session.exec(select(Cancion)).all())
            favoritos_count = len(session.exec(select(Favorito)).all())

            return {
                "usuarios": usuarios_count,
                "canciones": canciones_count,
                "favoritos": favoritos_count,
                "fecha_consulta": datetime.now(),
            }
    except Exception as e:
        logger.error(f"Error al obtener estadísticas: {e}")
        return {"error": str(e)}


# Funciones de utilidad para testing
def crear_db_test():
    """Crear base de datos para testing"""
    test_engine = create_engine(
        "sqlite:///./test_musica.db", connect_args={"check_same_thread": False}
    )
    SQLModel.metadata.create_all(test_engine)
    return test_engine


def limpiar_db_test():
    """Limpiar base de datos de testing"""
    test_engine = create_engine(
        "sqlite:///./test_musica.db", connect_args={"check_same_thread": False}
    )
    SQLModel.metadata.drop_all(test_engine)

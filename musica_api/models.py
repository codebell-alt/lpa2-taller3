"""
Modelos de datos para la API de Música.
Utiliza SQLModel para la integración con FastAPI y SQLAlchemy.
Creado por Isabella Ramírez Franco (@isabellaramirez)
"""

import re
from datetime import datetime

from pydantic import validator
from sqlmodel import Field, Relationship, SQLModel


class Usuario(SQLModel, table=True):
    """
    Modelo de Usuario en la base de datos.

    Atributos:
        id: Identificador único del usuario
        nombre: Nombre completo del usuario
        correo: Correo electrónico único
        fecha_registro: Fecha y hora de registro automática
    """

    __tablename__ = "usuarios"

    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(
        min_length=2,
        max_length=100,
        index=True,
        description="Nombre completo del usuario",
    )
    correo: str = Field(
        unique=True, index=True, description="Correo electrónico único del usuario"
    )
    fecha_registro: datetime = Field(
        default_factory=datetime.now, description="Fecha y hora de registro"
    )

    # Relación con favoritos
    favoritos: list["Favorito"] = Relationship(back_populates="usuario")

    @validator("correo")
    def validar_correo(cls, v):
        """Validar formato de correo electrónico"""
        if not v or "@" not in v or "." not in v:
            raise ValueError(
                "El correo debe tener un formato válido (ejemplo@dominio.com)"
            )

        # Validación con regex más robusta
        patron_email = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(patron_email, v):
            raise ValueError("El formato del correo electrónico no es válido")

        return v.lower().strip()

    @validator("nombre")
    def validar_nombre(cls, v):
        """Validar que el nombre solo contenga letras y espacios"""
        if not v or not v.strip():
            raise ValueError("El nombre no puede estar vacío")

        # Permitir letras, espacios y algunos caracteres especiales
        patron_nombre = r"^[a-zA-ZÀ-ÿ\u00f1\u00d1\s.-]+$"
        if not re.match(patron_nombre, v.strip()):
            raise ValueError("El nombre solo puede contener letras, espacios y guiones")

        return v.strip().title()


class Cancion(SQLModel, table=True):
    """
    Modelo de Canción en la base de datos.

    Atributos:
        id: Identificador único de la canción
        titulo: Título de la canción
        artista: Nombre del artista o banda
        album: Nombre del álbum
        duracion: Duración en segundos
        año: Año de lanzamiento
        genero: Género musical
        fecha_creacion: Fecha de creación del registro
    """

    __tablename__ = "canciones"

    id: int | None = Field(default=None, primary_key=True)
    titulo: str = Field(
        min_length=1, max_length=200, index=True, description="Título de la canción"
    )
    artista: str = Field(
        min_length=1,
        max_length=100,
        index=True,
        description="Nombre del artista o banda",
    )
    album: str = Field(min_length=1, max_length=200, description="Nombre del álbum")
    duracion: int = Field(
        gt=0,
        le=7200,  # Máximo 2 horas
        description="Duración en segundos",
    )
    año: int = Field(ge=1900, le=2030, description="Año de lanzamiento")
    genero: str = Field(
        min_length=1, max_length=50, index=True, description="Género musical"
    )
    fecha_creacion: datetime = Field(
        default_factory=datetime.now, description="Fecha de creación del registro"
    )

    # Relación con favoritos
    favoritos: list["Favorito"] = Relationship(back_populates="cancion")

    @validator("duracion")
    def validar_duracion(cls, v):
        """Validar que la duración esté en un rango razonable"""
        if v <= 0:
            raise ValueError("La duración debe ser mayor a 0 segundos")
        if v > 7200:  # 2 horas
            raise ValueError("La duración no puede ser mayor a 2 horas (7200 segundos)")
        return v

    @validator("año")
    def validar_año(cls, v):
        """Validar que el año esté en un rango razonable"""
        año_actual = datetime.now().year
        if v < 1900:
            raise ValueError("El año no puede ser anterior a 1900")
        if v > año_actual + 1:
            raise ValueError(f"El año no puede ser posterior a {año_actual + 1}")
        return v

    @validator("titulo", "artista", "album", "genero")
    def validar_campos_texto(cls, v):
        """Validar campos de texto generales"""
        if not v or not v.strip():
            raise ValueError("Este campo no puede estar vacío")
        return v.strip()


class Favorito(SQLModel, table=True):
    """
    Modelo de Favorito en la base de datos.
    Representa la relación muchos a muchos entre usuarios y canciones.

    Atributos:
        id: Identificador único del favorito
        id_usuario: ID del usuario (clave foránea)
        id_cancion: ID de la canción (clave foránea)
        fecha_marcado: Fecha cuando se marcó como favorito
    """

    __tablename__ = "favoritos"

    id: int | None = Field(default=None, primary_key=True)
    id_usuario: int = Field(
        foreign_key="usuarios.id", description="ID del usuario que marcó el favorito"
    )
    id_cancion: int = Field(
        foreign_key="canciones.id", description="ID de la canción marcada como favorita"
    )
    fecha_marcado: datetime = Field(
        default_factory=datetime.now,
        description="Fecha y hora cuando se marcó como favorito",
    )

    # Relaciones
    usuario: Usuario = Relationship(back_populates="favoritos")
    cancion: Cancion = Relationship(back_populates="favoritos")


# ============================================================================
# MODELOS PYDANTIC PARA LAS APIS (Request/Response)
# ============================================================================


class UsuarioCreate(SQLModel):
    """Modelo para crear usuarios - Request"""

    nombre: str = Field(
        min_length=2, max_length=100, description="Nombre completo del usuario"
    )
    correo: str = Field(description="Correo electrónico único")


class UsuarioRead(SQLModel):
    """Modelo para leer usuarios - Response"""

    id: int
    nombre: str
    correo: str
    fecha_registro: datetime

    class Config:
        from_attributes = True


class UsuarioUpdate(SQLModel):
    """Modelo para actualizar usuarios - Request"""

    nombre: str | None = Field(
        None, min_length=2, max_length=100, description="Nuevo nombre del usuario"
    )
    correo: str | None = Field(None, description="Nuevo correo electrónico")


class CancionCreate(SQLModel):
    """Modelo para crear canciones - Request"""

    titulo: str = Field(
        min_length=1, max_length=200, description="Título de la canción"
    )
    artista: str = Field(min_length=1, max_length=100, description="Nombre del artista")
    album: str = Field(min_length=1, max_length=200, description="Nombre del álbum")
    duracion: int = Field(gt=0, le=7200, description="Duración en segundos")
    año: int = Field(ge=1900, le=2030, description="Año de lanzamiento")
    genero: str = Field(min_length=1, max_length=50, description="Género musical")


class CancionRead(SQLModel):
    """Modelo para leer canciones - Response"""

    id: int
    titulo: str
    artista: str
    album: str
    duracion: int
    año: int
    genero: str
    fecha_creacion: datetime

    class Config:
        from_attributes = True


class CancionUpdate(SQLModel):
    """Modelo para actualizar canciones - Request"""

    titulo: str | None = Field(None, min_length=1, max_length=200)
    artista: str | None = Field(None, min_length=1, max_length=100)
    album: str | None = Field(None, min_length=1, max_length=200)
    duracion: int | None = Field(None, gt=0, le=7200)
    año: int | None = Field(None, ge=1900, le=2030)
    genero: str | None = Field(None, min_length=1, max_length=50)


class FavoritoCreate(SQLModel):
    """Modelo para crear favoritos - Request"""

    id_usuario: int = Field(description="ID del usuario")
    id_cancion: int = Field(description="ID de la canción")


class FavoritoRead(SQLModel):
    """Modelo para leer favoritos con información completa - Response"""

    id: int
    id_usuario: int
    id_cancion: int
    fecha_marcado: datetime
    usuario: UsuarioRead
    cancion: CancionRead

    class Config:
        from_attributes = True


class FavoritoSimple(SQLModel):
    """Modelo simple para favoritos - Response"""

    id: int
    id_usuario: int
    id_cancion: int
    fecha_marcado: datetime

    class Config:
        from_attributes = True


# ============================================================================
# MODELOS PARA BÚSQUEDAS Y FILTROS
# ============================================================================


class CancionFiltros(SQLModel):
    """Modelo para filtros de búsqueda de canciones"""

    titulo: str | None = Field(None, description="Filtrar por título")
    artista: str | None = Field(None, description="Filtrar por artista")
    genero: str | None = Field(None, description="Filtrar por género")
    año_desde: int | None = Field(None, description="Año mínimo")
    año_hasta: int | None = Field(None, description="Año máximo")


# ============================================================================
# MODELOS DE RESPUESTA GENERALES
# ============================================================================


class MensajeRespuesta(SQLModel):
    """Modelo para respuestas con mensaje"""

    mensaje: str
    exito: bool = True


class ErrorRespuesta(SQLModel):
    """Modelo para respuestas de error"""

    error: str
    detalle: str | None = None
    exito: bool = False

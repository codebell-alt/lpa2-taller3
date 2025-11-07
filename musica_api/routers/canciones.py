"""
Router para canciones - Endpoints CRUD completos con búsqueda
API de Música - Desarrollada por Isabella Ramírez Franco (@codebell-alt)
"""


from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, func, or_, select

from musica_api.database import get_session
from musica_api.models import (
    Cancion,
    CancionCreate,
    CancionRead,
    CancionUpdate,
    MensajeRespuesta,
)
from musica_api.pagination import PaginatedResponse, PaginationParams

# Crear el router con prefijo y etiquetas
router = APIRouter(
    prefix="/api/canciones",
    tags=["Canciones"],
    responses={
        404: {"description": "Canción no encontrada"},
        422: {"description": "Error de validación"},
    },
)


@router.get("/", response_model=PaginatedResponse[CancionRead])
def listar_canciones(
    page: int = Query(1, ge=1, description="Número de página"),
    size: int = Query(10, ge=1, le=100, description="Elementos por página"),
    genero: str | None = Query(None, description="Filtrar por género"),
    año_desde: int | None = Query(None, ge=1900, description="Año mínimo"),
    año_hasta: int | None = Query(None, le=2030, description="Año máximo"),
    session: Session = Depends(get_session),
):
    """
    Listar canciones con paginación y filtros opcionales.

    - **page**: Número de página (empezando en 1)
    - **size**: Número de elementos por página (1-100)
    - **genero**: Filtrar por género musical
    - **año_desde**: Filtrar canciones desde este año
    - **año_hasta**: Filtrar canciones hasta este año
    """
    # Crear parámetros de paginación
    pagination_params = PaginationParams(page=page, size=size)

    # Construir consulta base
    base_statement = select(Cancion)

    # Aplicar filtros si se proporcionan
    if genero:
        base_statement = base_statement.where(Cancion.genero.ilike(f"%{genero}%"))

    if año_desde:
        base_statement = base_statement.where(Cancion.año >= año_desde)

    if año_hasta:
        base_statement = base_statement.where(Cancion.año <= año_hasta)

    # Obtener total de canciones con filtros
    total_statement = select(func.count(Cancion.id))
    if genero:
        total_statement = total_statement.where(Cancion.genero.ilike(f"%{genero}%"))
    if año_desde:
        total_statement = total_statement.where(Cancion.año >= año_desde)
    if año_hasta:
        total_statement = total_statement.where(Cancion.año <= año_hasta)

    total = session.exec(total_statement).one()

    # Aplicar paginación y obtener canciones
    statement = base_statement.offset(pagination_params.offset).limit(
        pagination_params.limit
    )
    canciones = session.exec(statement).all()

    # Crear respuesta paginada
    return PaginatedResponse.create(
        items=canciones,
        total=total,
        page=page,
        size=size,
    )


@router.post("/", response_model=CancionRead, status_code=status.HTTP_201_CREATED)
def crear_cancion(cancion: CancionCreate, session: Session = Depends(get_session)):
    """
    Crear una nueva canción.

    - **titulo**: Título de la canción
    - **artista**: Nombre del artista o banda
    - **album**: Nombre del álbum
    - **duracion**: Duración en segundos
    - **año**: Año de lanzamiento
    - **genero**: Género musical
    """
    # Crear la nueva canción
    db_cancion = Cancion.model_validate(cancion)
    session.add(db_cancion)
    session.commit()
    session.refresh(db_cancion)

    return db_cancion


@router.get("/{cancion_id}", response_model=CancionRead)
def obtener_cancion(cancion_id: int, session: Session = Depends(get_session)):
    """
    Obtener una canción específica por ID.

    - **cancion_id**: ID único de la canción
    """
    cancion = session.get(Cancion, cancion_id)
    if not cancion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Canción con ID {cancion_id} no encontrada",
        )
    return cancion


@router.put("/{cancion_id}", response_model=CancionRead)
def actualizar_cancion(
    cancion_id: int,
    cancion_update: CancionUpdate,
    session: Session = Depends(get_session),
):
    """
    Actualizar una canción existente.

    - **cancion_id**: ID único de la canción
    - Campos opcionales: titulo, artista, album, duracion, año, genero
    """
    # Verificar que la canción existe
    cancion = session.get(Cancion, cancion_id)
    if not cancion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Canción con ID {cancion_id} no encontrada",
        )

    # Actualizar solo los campos proporcionados
    cancion_data = cancion_update.model_dump(exclude_unset=True)
    for field, value in cancion_data.items():
        setattr(cancion, field, value)

    session.add(cancion)
    session.commit()
    session.refresh(cancion)

    return cancion


@router.delete("/{cancion_id}", response_model=MensajeRespuesta)
def eliminar_cancion(cancion_id: int, session: Session = Depends(get_session)):
    """
    Eliminar una canción.

    - **cancion_id**: ID único de la canción a eliminar
    """
    cancion = session.get(Cancion, cancion_id)
    if not cancion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Canción con ID {cancion_id} no encontrada",
        )

    session.delete(cancion)
    session.commit()

    return MensajeRespuesta(
        mensaje=f"Canción '{cancion.titulo}' de {cancion.artista} eliminada exitosamente",
        exito=True,
    )


@router.get("/buscar/avanzada", response_model=list[CancionRead])
def buscar_canciones(
    q: str | None = Query(None, description="Término de búsqueda general"),
    titulo: str | None = Query(None, description="Buscar en títulos"),
    artista: str | None = Query(None, description="Buscar por artista"),
    album: str | None = Query(None, description="Buscar por álbum"),
    genero: str | None = Query(None, description="Buscar por género"),
    duracion_min: int | None = Query(
        None, ge=1, description="Duración mínima en segundos"
    ),
    duracion_max: int | None = Query(
        None, le=7200, description="Duración máxima en segundos"
    ),
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(50, ge=1, le=500, description="Límite de registros"),
    session: Session = Depends(get_session),
):
    """
    Búsqueda avanzada de canciones con múltiples criterios.

    - **q**: Búsqueda general en título, artista y álbum
    - **titulo**: Buscar específicamente en títulos
    - **artista**: Buscar específicamente por artista
    - **album**: Buscar específicamente por álbum
    - **genero**: Filtrar por género
    - **duracion_min/max**: Filtrar por rango de duración
    """
    statement = select(Cancion)

    # Búsqueda general
    if q:
        search_term = f"%{q}%"
        statement = statement.where(
            or_(
                Cancion.titulo.ilike(search_term),
                Cancion.artista.ilike(search_term),
                Cancion.album.ilike(search_term),
            )
        )

    # Búsquedas específicas
    if titulo:
        statement = statement.where(Cancion.titulo.ilike(f"%{titulo}%"))

    if artista:
        statement = statement.where(Cancion.artista.ilike(f"%{artista}%"))

    if album:
        statement = statement.where(Cancion.album.ilike(f"%{album}%"))

    if genero:
        statement = statement.where(Cancion.genero.ilike(f"%{genero}%"))

    if duracion_min:
        statement = statement.where(Cancion.duracion >= duracion_min)

    if duracion_max:
        statement = statement.where(Cancion.duracion <= duracion_max)

    # Aplicar paginación
    statement = statement.offset(skip).limit(limit)

    canciones = session.exec(statement).all()
    return canciones


@router.get("/generos/lista")
def listar_generos(session: Session = Depends(get_session)):
    """
    Obtener lista de todos los géneros únicos disponibles.
    """
    result = session.exec(select(Cancion.genero).distinct())
    generos = list(result.all())

    return {"total_generos": len(generos), "generos": sorted(generos)}


@router.get("/artistas/lista")
def listar_artistas(session: Session = Depends(get_session)):
    """
    Obtener lista de todos los artistas únicos.
    """
    result = session.exec(select(Cancion.artista).distinct())
    artistas = list(result.all())

    return {"total_artistas": len(artistas), "artistas": sorted(artistas)}


@router.get("/estadisticas/resumen")
def obtener_estadisticas_canciones(session: Session = Depends(get_session)):
    """
    Obtener estadísticas básicas de canciones.
    """
    total_canciones = len(session.exec(select(Cancion)).all())

    # Canción más larga y más corta
    cancion_mas_larga = session.exec(
        select(Cancion).order_by(Cancion.duracion.desc())
    ).first()

    cancion_mas_corta = session.exec(
        select(Cancion).order_by(Cancion.duracion.asc())
    ).first()

    # Últimas canciones agregadas
    ultimas_canciones = session.exec(
        select(Cancion).order_by(Cancion.fecha_creacion.desc()).limit(5)
    ).all()

    return {
        "total_canciones": total_canciones,
        "cancion_mas_larga": {
            "titulo": cancion_mas_larga.titulo if cancion_mas_larga else None,
            "artista": cancion_mas_larga.artista if cancion_mas_larga else None,
            "duracion": cancion_mas_larga.duracion if cancion_mas_larga else None,
        }
        if cancion_mas_larga
        else None,
        "cancion_mas_corta": {
            "titulo": cancion_mas_corta.titulo if cancion_mas_corta else None,
            "artista": cancion_mas_corta.artista if cancion_mas_corta else None,
            "duracion": cancion_mas_corta.duracion if cancion_mas_corta else None,
        }
        if cancion_mas_corta
        else None,
        "ultimas_agregadas": [
            {
                "id": cancion.id,
                "titulo": cancion.titulo,
                "artista": cancion.artista,
                "fecha_creacion": cancion.fecha_creacion,
            }
            for cancion in ultimas_canciones
        ],
    }

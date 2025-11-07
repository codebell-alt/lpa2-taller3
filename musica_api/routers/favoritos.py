"""
Router para favoritos - Gestión de relaciones usuario-canción
API de Música - Desarrollada por Isabella Ramírez Franco (@codebell-alt)
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, func, select

from musica_api.database import get_session
from musica_api.models import (
    Cancion,
    CancionRead,
    Favorito,
    FavoritoCreate,
    FavoritoRead,
    FavoritoSimple,
    MensajeRespuesta,
    Usuario,
    UsuarioRead,
)
from musica_api.pagination import PaginatedResponse, PaginationParams

# Crear el router con prefijo y etiquetas
router = APIRouter(
    prefix="/api/favoritos",
    tags=["Favoritos"],
    responses={
        404: {"description": "Favorito no encontrado"},
        422: {"description": "Error de validación"},
    },
)


@router.get("/", response_model=PaginatedResponse[FavoritoRead])
def listar_favoritos(
    page: int = Query(1, ge=1, description="Número de página"),
    size: int = Query(10, ge=1, le=100, description="Elementos por página"),
    usuario_id: int | None = Query(None, description="Filtrar por ID de usuario"),
    session: Session = Depends(get_session),
):
    """
    Listar todos los favoritos con información completa.

    - **page**: Número de página (empezando en 1)
    - **size**: Número de elementos por página (1-100)
    - **usuario_id**: Filtrar favoritos de un usuario específico
    """
    # Crear parámetros de paginación
    pagination_params = PaginationParams(page=page, size=size)

    # Construir consulta base
    base_statement = select(Favorito)

    # Filtrar por usuario si se especifica
    if usuario_id:
        base_statement = base_statement.where(Favorito.id_usuario == usuario_id)

    # Obtener total de favoritos con filtros
    total_statement = select(func.count(Favorito.id))
    if usuario_id:
        total_statement = total_statement.where(Favorito.id_usuario == usuario_id)

    total = session.exec(total_statement).one()

    # Aplicar paginación y obtener favoritos
    statement = base_statement.offset(pagination_params.offset).limit(
        pagination_params.limit
    )
    favoritos = session.exec(statement).all()

    # Cargar las relaciones manualmente
    result = []
    for favorito in favoritos:
        usuario = session.get(Usuario, favorito.id_usuario)
        cancion = session.get(Cancion, favorito.id_cancion)

        favorito_completo = FavoritoRead(
            id=favorito.id,
            id_usuario=favorito.id_usuario,
            id_cancion=favorito.id_cancion,
            fecha_marcado=favorito.fecha_marcado,
            usuario=UsuarioRead(
                id=usuario.id,
                nombre=usuario.nombre,
                correo=usuario.correo,
                fecha_registro=usuario.fecha_registro,
            ),
            cancion=CancionRead(
                id=cancion.id,
                titulo=cancion.titulo,
                artista=cancion.artista,
                album=cancion.album,
                duracion=cancion.duracion,
                año=cancion.año,
                genero=cancion.genero,
                fecha_creacion=cancion.fecha_creacion,
            ),
        )
        result.append(favorito_completo)

    # Crear respuesta paginada
    return PaginatedResponse.create(
        items=result,
        total=total,
        page=page,
        size=size,
    )


@router.post("/", response_model=FavoritoSimple, status_code=status.HTTP_201_CREATED)
def marcar_favorito(favorito: FavoritoCreate, session: Session = Depends(get_session)):
    """
    Marcar una canción como favorita para un usuario.

    - **id_usuario**: ID del usuario
    - **id_cancion**: ID de la canción
    """
    # Verificar que el usuario existe
    usuario = session.get(Usuario, favorito.id_usuario)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {favorito.id_usuario} no encontrado",
        )

    # Verificar que la canción existe
    cancion = session.get(Cancion, favorito.id_cancion)
    if not cancion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Canción con ID {favorito.id_cancion} no encontrada",
        )

    # Verificar que no sea ya un favorito
    existing_favorito = session.exec(
        select(Favorito).where(
            Favorito.id_usuario == favorito.id_usuario,
            Favorito.id_cancion == favorito.id_cancion,
        )
    ).first()

    if existing_favorito:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La canción '{cancion.titulo}' ya está marcada como favorita para este usuario",
        )

    # Crear el nuevo favorito
    db_favorito = Favorito.model_validate(favorito)
    session.add(db_favorito)
    session.commit()
    session.refresh(db_favorito)

    return db_favorito


@router.get("/{favorito_id}", response_model=FavoritoRead)
def obtener_favorito(favorito_id: int, session: Session = Depends(get_session)):
    """
    Obtener un favorito específico por ID con información completa.

    - **favorito_id**: ID único del favorito
    """
    favorito = session.get(Favorito, favorito_id)
    if not favorito:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Favorito con ID {favorito_id} no encontrado",
        )

    # Cargar las relaciones
    usuario = session.get(Usuario, favorito.id_usuario)
    cancion = session.get(Cancion, favorito.id_cancion)

    return FavoritoRead(
        id=favorito.id,
        id_usuario=favorito.id_usuario,
        id_cancion=favorito.id_cancion,
        fecha_marcado=favorito.fecha_marcado,
        usuario=UsuarioRead(
            id=usuario.id,
            nombre=usuario.nombre,
            correo=usuario.correo,
            fecha_registro=usuario.fecha_registro,
        ),
        cancion=CancionRead(
            id=cancion.id,
            titulo=cancion.titulo,
            artista=cancion.artista,
            album=cancion.album,
            duracion=cancion.duracion,
            año=cancion.año,
            genero=cancion.genero,
            fecha_creacion=cancion.fecha_creacion,
        ),
    )


@router.delete("/{favorito_id}", response_model=MensajeRespuesta)
def quitar_favorito(favorito_id: int, session: Session = Depends(get_session)):
    """
    Quitar una canción de favoritos.

    - **favorito_id**: ID único del favorito a eliminar
    """
    favorito = session.get(Favorito, favorito_id)
    if not favorito:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Favorito con ID {favorito_id} no encontrado",
        )

    # Obtener información de la canción para el mensaje
    cancion = session.get(Cancion, favorito.id_cancion)

    session.delete(favorito)
    session.commit()

    return MensajeRespuesta(
        mensaje=f"Canción '{cancion.titulo}' eliminada de favoritos", exito=True
    )


# Endpoints específicos para gestión por usuario
@router.get("/usuario/{usuario_id}", response_model=list[CancionRead])
def obtener_favoritos_usuario(
    usuario_id: int,
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Límite de registros"),
    session: Session = Depends(get_session),
):
    """
    Obtener todas las canciones favoritas de un usuario específico.

    - **usuario_id**: ID del usuario
    """
    # Verificar que el usuario existe
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {usuario_id} no encontrado",
        )

    # Obtener los favoritos del usuario
    statement = (
        select(Favorito)
        .where(Favorito.id_usuario == usuario_id)
        .offset(skip)
        .limit(limit)
    )
    favoritos = session.exec(statement).all()

    # Obtener las canciones correspondientes
    canciones = []
    for favorito in favoritos:
        cancion = session.get(Cancion, favorito.id_cancion)
        if cancion:
            canciones.append(cancion)

    return canciones


@router.post(
    "/usuario/{usuario_id}/cancion/{cancion_id}", response_model=FavoritoSimple
)
def marcar_favorito_directo(
    usuario_id: int, cancion_id: int, session: Session = Depends(get_session)
):
    """
    Marcar una canción como favorita usando IDs directos.

    - **usuario_id**: ID del usuario
    - **cancion_id**: ID de la canción
    """
    # Crear el favorito usando los IDs de la URL
    favorito_data = FavoritoCreate(id_usuario=usuario_id, id_cancion=cancion_id)
    return marcar_favorito(favorito_data, session)


@router.delete(
    "/usuario/{usuario_id}/cancion/{cancion_id}", response_model=MensajeRespuesta
)
def quitar_favorito_directo(
    usuario_id: int, cancion_id: int, session: Session = Depends(get_session)
):
    """
    Quitar una canción de favoritos usando IDs directos.

    - **usuario_id**: ID del usuario
    - **cancion_id**: ID de la canción
    """
    # Buscar el favorito
    favorito = session.exec(
        select(Favorito).where(
            Favorito.id_usuario == usuario_id, Favorito.id_cancion == cancion_id
        )
    ).first()

    if not favorito:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe favorito para usuario {usuario_id} y canción {cancion_id}",
        )

    # Usar la función de eliminar existente
    return quitar_favorito(favorito.id, session)


@router.get("/verificar/{usuario_id}/{cancion_id}")
def verificar_es_favorito(
    usuario_id: int, cancion_id: int, session: Session = Depends(get_session)
):
    """
    Verificar si una canción es favorita para un usuario.

    - **usuario_id**: ID del usuario
    - **cancion_id**: ID de la canción
    """
    favorito = session.exec(
        select(Favorito).where(
            Favorito.id_usuario == usuario_id, Favorito.id_cancion == cancion_id
        )
    ).first()

    return {
        "es_favorito": favorito is not None,
        "usuario_id": usuario_id,
        "cancion_id": cancion_id,
        "fecha_marcado": favorito.fecha_marcado if favorito else None,
    }


@router.get("/estadisticas/resumen")
def obtener_estadisticas_favoritos(session: Session = Depends(get_session)):
    """
    Obtener estadísticas básicas de favoritos.
    """
    total_favoritos = len(session.exec(select(Favorito)).all())

    # Usuario con más favoritos
    statement = select(Favorito.id_usuario).group_by(Favorito.id_usuario)
    usuarios_favoritos = session.exec(statement).all()

    # Canción más favorita
    statement = select(Favorito.id_cancion).group_by(Favorito.id_cancion)
    canciones_favoritas = session.exec(statement).all()

    # Últimos favoritos marcados
    ultimos_favoritos = session.exec(
        select(Favorito).order_by(Favorito.fecha_marcado.desc()).limit(5)
    ).all()

    return {
        "total_favoritos": total_favoritos,
        "usuarios_con_favoritos": len(set(usuarios_favoritos)),
        "canciones_marcadas": len(set(canciones_favoritas)),
        "ultimos_favoritos": [
            {
                "id": favorito.id,
                "usuario_id": favorito.id_usuario,
                "cancion_id": favorito.id_cancion,
                "fecha_marcado": favorito.fecha_marcado,
            }
            for favorito in ultimos_favoritos
        ],
    }

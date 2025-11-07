"""
Router para usuarios - Endpoints CRUD completos
API de Música - Desarrollada por Isabella Ramírez Franco (@codebell-alt)
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, func, select

from musica_api.database import get_session
from musica_api.logging_config import get_logger
from musica_api.middleware import log_endpoint_access, log_validation_error
from musica_api.models import (
    MensajeRespuesta,
    Usuario,
    UsuarioCreate,
    UsuarioRead,
    UsuarioUpdate,
)
from musica_api.pagination import PaginatedResponse, PaginationParams

# Logger específico para usuarios
logger = get_logger(__name__)

# Crear el router con prefijo y etiquetas
router = APIRouter(
    prefix="/api/usuarios",
    tags=["Usuarios"],
    responses={
        404: {"description": "Usuario no encontrado"},
        422: {"description": "Error de validación"},
    },
)


@router.get("/", response_model=PaginatedResponse[UsuarioRead])
def listar_usuarios(
    page: int = Query(1, ge=1, description="Número de página"),
    size: int = Query(10, ge=1, le=100, description="Elementos por página"),
    session: Session = Depends(get_session),
):
    """
    Listar todos los usuarios con paginación.

    - **page**: Número de página (empezando en 1)
    - **size**: Número de elementos por página (1-100)
    """
    # Crear parámetros de paginación
    pagination_params = PaginationParams(page=page, size=size)

    # Obtener total de usuarios
    total_statement = select(func.count(Usuario.id))
    total = session.exec(total_statement).one()

    # Obtener usuarios de la página actual
    statement = (
        select(Usuario).offset(pagination_params.offset).limit(pagination_params.limit)
    )
    usuarios = session.exec(statement).all()

    # Crear respuesta paginada
    return PaginatedResponse.create(
        items=usuarios,
        total=total,
        page=page,
        size=size,
    )


@router.post("/", response_model=UsuarioRead, status_code=status.HTTP_201_CREATED)
def crear_usuario(usuario: UsuarioCreate, session: Session = Depends(get_session)):
    """
    Crear un nuevo usuario.

    - **nombre**: Nombre completo del usuario
    - **correo**: Correo electrónico único
    """
    # Log del intento de creación
    log_endpoint_access("usuarios", "POST")
    logger.info(f"Intento de crear usuario con correo: {usuario.correo}")

    # Verificar si el correo ya existe
    existing_user = session.exec(
        select(Usuario).where(Usuario.correo == usuario.correo)
    ).first()

    if existing_user:
        log_validation_error("correo", usuario.correo, "Correo ya existe")
        logger.warning(f"Intento de crear usuario duplicado: {usuario.correo}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un usuario con el correo: {usuario.correo}",
        )

    try:
        # Crear el nuevo usuario
        db_usuario = Usuario.model_validate(usuario)
        session.add(db_usuario)
        session.commit()
        session.refresh(db_usuario)

        logger.info(
            f"Usuario creado exitosamente - ID: {db_usuario.id}, Correo: {db_usuario.correo}"
        )
        return db_usuario

    except Exception as e:
        logger.error(f"Error al crear usuario: {str(e)}")
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al crear usuario",
        )


@router.get("/{usuario_id}", response_model=UsuarioRead)
def obtener_usuario(usuario_id: int, session: Session = Depends(get_session)):
    """
    Obtener un usuario específico por ID.

    - **usuario_id**: ID único del usuario
    """
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {usuario_id} no encontrado",
        )
    return usuario


@router.put("/{usuario_id}", response_model=UsuarioRead)
def actualizar_usuario(
    usuario_id: int,
    usuario_update: UsuarioUpdate,
    session: Session = Depends(get_session),
):
    """
    Actualizar un usuario existente.

    - **usuario_id**: ID único del usuario
    - **nombre**: Nuevo nombre del usuario (opcional)
    - **correo**: Nuevo correo del usuario (opcional)
    """
    # Verificar que el usuario existe
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {usuario_id} no encontrado",
        )

    # Si se va a actualizar el correo, verificar que no exista
    if usuario_update.correo and usuario_update.correo != usuario.correo:
        existing_user = session.exec(
            select(Usuario).where(Usuario.correo == usuario_update.correo)
        ).first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un usuario con el correo: {usuario_update.correo}",
            )

    # Actualizar solo los campos proporcionados
    usuario_data = usuario_update.model_dump(exclude_unset=True)
    for field, value in usuario_data.items():
        setattr(usuario, field, value)

    session.add(usuario)
    session.commit()
    session.refresh(usuario)

    return usuario


@router.delete("/{usuario_id}", response_model=MensajeRespuesta)
def eliminar_usuario(usuario_id: int, session: Session = Depends(get_session)):
    """
    Eliminar un usuario.

    - **usuario_id**: ID único del usuario a eliminar
    """
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {usuario_id} no encontrado",
        )

    session.delete(usuario)
    session.commit()

    return MensajeRespuesta(
        mensaje=f"Usuario '{usuario.nombre}' eliminado exitosamente", exito=True
    )


@router.get("/{usuario_id}/existe")
def verificar_usuario_existe(usuario_id: int, session: Session = Depends(get_session)):
    """
    Verificar si un usuario existe por ID.

    - **usuario_id**: ID único del usuario
    """
    usuario = session.get(Usuario, usuario_id)
    return {"existe": usuario is not None, "usuario_id": usuario_id}


@router.get("/buscar/por-correo")
def buscar_usuario_por_correo(
    correo: str = Query(..., description="Correo electrónico a buscar"),
    session: Session = Depends(get_session),
):
    """
    Buscar usuario por correo electrónico.

    - **correo**: Correo electrónico exacto a buscar
    """
    usuario = session.exec(select(Usuario).where(Usuario.correo == correo)).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró usuario con el correo: {correo}",
        )

    return usuario


@router.get("/estadisticas/resumen")
def obtener_estadisticas_usuarios(session: Session = Depends(get_session)):
    """
    Obtener estadísticas básicas de usuarios.
    """
    total_usuarios = len(session.exec(select(Usuario)).all())

    # Obtener los últimos 5 usuarios registrados
    ultimos_usuarios = session.exec(
        select(Usuario).order_by(Usuario.fecha_registro.desc()).limit(5)
    ).all()

    return {
        "total_usuarios": total_usuarios,
        "ultimos_registros": [
            {
                "id": usuario.id,
                "nombre": usuario.nombre,
                "fecha_registro": usuario.fecha_registro,
            }
            for usuario in ultimos_usuarios
        ],
    }

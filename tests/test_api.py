"""
Pruebas unitarias para la API de Música
Desarrollado por Isabella Ramírez Franco (@codebell-alt)

Este archivo contiene todas las pruebas para verificar el funcionamiento
correcto de los endpoints de la API REST.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

# Importar la aplicación y dependencias
from main import app
from musica_api.database import get_session

# ============================================================================
# CONFIGURACIÓN DE PRUEBAS
# ============================================================================


# Crear motor de base de datos en memoria para pruebas
@pytest.fixture(name="session")
def session_fixture():
    """Crear una sesión de base de datos en memoria para pruebas"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Crear un cliente de prueba con base de datos en memoria"""

    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client

    app.dependency_overrides.clear()


# Datos de prueba
@pytest.fixture
def usuario_data():
    return {"nombre": "Usuario Test", "correo": "test@ejemplo.com"}


@pytest.fixture
def cancion_data():
    return {
        "titulo": "Canción Test",
        "artista": "Artista Test",
        "album": "Álbum Test",
        "duracion": 180,
        "año": 2023,
        "genero": "Rock",
    }


# ============================================================================
# PRUEBAS DE ENDPOINTS PRINCIPALES
# ============================================================================


def test_root_endpoint(client: TestClient):
    """Probar endpoint raíz de la API"""
    response = client.get("/")
    assert response.status_code == 200

    data = response.json()
    assert "mensaje" in data
    assert "version" in data
    assert "desarrollador" in data
    assert data["desarrollador"]["nombre"] == "Isabella Ramírez Franco"
    assert data["desarrollador"]["github"] == "@codebell-alt"


def test_health_endpoint(client: TestClient):
    """Probar endpoint de health check"""
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert "status" in data
    assert "database" in data
    assert "uptime_seconds" in data
    assert "developer" in data
    assert data["developer"] == "Isabella Ramírez Franco"


# ============================================================================
# PRUEBAS DE USUARIOS
# ============================================================================


def test_crear_usuario(client: TestClient, usuario_data):
    """Probar creación de usuario"""
    response = client.post("/api/usuarios", json=usuario_data)
    assert response.status_code == 201

    data = response.json()
    assert data["nombre"] == usuario_data["nombre"]
    assert data["correo"] == usuario_data["correo"]
    assert "id" in data
    assert "fecha_registro" in data


def test_crear_usuario_email_duplicado(client: TestClient, usuario_data):
    """Probar que no se puede crear usuario con email duplicado"""
    # Crear primer usuario
    client.post("/api/usuarios", json=usuario_data)

    # Intentar crear usuario con mismo email
    response = client.post("/api/usuarios", json=usuario_data)
    assert response.status_code == 400


def test_listar_usuarios(client: TestClient, usuario_data):
    """Probar listado de usuarios"""
    # Crear usuario primero
    client.post("/api/usuarios", json=usuario_data)

    # Listar usuarios
    response = client.get("/api/usuarios")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_obtener_usuario(client: TestClient, usuario_data):
    """Probar obtener usuario específico"""
    # Crear usuario
    create_response = client.post("/api/usuarios", json=usuario_data)
    user_id = create_response.json()["id"]

    # Obtener usuario
    response = client.get(f"/api/usuarios/{user_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == user_id
    assert data["correo"] == usuario_data["correo"]


def test_actualizar_usuario(client: TestClient, usuario_data):
    """Probar actualización de usuario"""
    # Crear usuario
    create_response = client.post("/api/usuarios", json=usuario_data)
    user_id = create_response.json()["id"]

    # Datos actualizados
    updated_data = {"nombre": "Nombre Actualizado", "correo": "actualizado@ejemplo.com"}

    # Actualizar usuario
    response = client.put(f"/api/usuarios/{user_id}", json=updated_data)
    assert response.status_code == 200

    data = response.json()
    assert data["nombre"] == updated_data["nombre"]
    assert data["correo"] == updated_data["correo"]


def test_eliminar_usuario(client: TestClient, usuario_data):
    """Probar eliminación de usuario"""
    # Crear usuario
    create_response = client.post("/api/usuarios", json=usuario_data)
    user_id = create_response.json()["id"]

    # Eliminar usuario
    response = client.delete(f"/api/usuarios/{user_id}")
    assert response.status_code == 200

    # Verificar que ya no existe
    get_response = client.get(f"/api/usuarios/{user_id}")
    assert get_response.status_code == 404


# ============================================================================
# PRUEBAS DE CANCIONES
# ============================================================================


def test_crear_cancion(client: TestClient, cancion_data):
    """Probar creación de canción"""
    response = client.post("/api/canciones", json=cancion_data)
    assert response.status_code == 201

    data = response.json()
    assert data["titulo"] == cancion_data["titulo"]
    assert data["artista"] == cancion_data["artista"]
    assert data["duracion"] == cancion_data["duracion"]
    assert "id" in data


def test_listar_canciones(client: TestClient, cancion_data):
    """Probar listado de canciones"""
    # Crear canción
    client.post("/api/canciones", json=cancion_data)

    # Listar canciones
    response = client.get("/api/canciones")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_buscar_canciones(client: TestClient, cancion_data):
    """Probar búsqueda de canciones"""
    # Crear canción
    client.post("/api/canciones", json=cancion_data)

    # Buscar por título
    response = client.get(f"/api/canciones/buscar?titulo={cancion_data['titulo']}")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_actualizar_cancion(client: TestClient, cancion_data):
    """Probar actualización de canción"""
    # Crear canción
    create_response = client.post("/api/canciones", json=cancion_data)
    cancion_id = create_response.json()["id"]

    # Datos actualizados
    updated_data = cancion_data.copy()
    updated_data["titulo"] = "Título Actualizado"

    # Actualizar canción
    response = client.put(f"/api/canciones/{cancion_id}", json=updated_data)
    assert response.status_code == 200

    data = response.json()
    assert data["titulo"] == updated_data["titulo"]


def test_eliminar_cancion(client: TestClient, cancion_data):
    """Probar eliminación de canción"""
    # Crear canción
    create_response = client.post("/api/canciones", json=cancion_data)
    cancion_id = create_response.json()["id"]

    # Eliminar canción
    response = client.delete(f"/api/canciones/{cancion_id}")
    assert response.status_code == 200


# ============================================================================
# PRUEBAS DE FAVORITOS
# ============================================================================


def test_crear_favorito(client: TestClient, usuario_data, cancion_data):
    """Probar creación de favorito"""
    # Crear usuario y canción
    user_response = client.post("/api/usuarios", json=usuario_data)
    song_response = client.post("/api/canciones", json=cancion_data)

    user_id = user_response.json()["id"]
    song_id = song_response.json()["id"]

    # Crear favorito
    favorito_data = {"id_usuario": user_id, "id_cancion": song_id}

    response = client.post("/api/favoritos", json=favorito_data)
    assert response.status_code == 201

    data = response.json()
    assert data["id_usuario"] == user_id
    assert data["id_cancion"] == song_id


def test_listar_favoritos(client: TestClient, usuario_data, cancion_data):
    """Probar listado de favoritos"""
    # Crear usuario, canción y favorito
    user_response = client.post("/api/usuarios", json=usuario_data)
    song_response = client.post("/api/canciones", json=cancion_data)

    user_id = user_response.json()["id"]
    song_id = song_response.json()["id"]

    favorito_data = {"id_usuario": user_id, "id_cancion": song_id}
    client.post("/api/favoritos", json=favorito_data)

    # Listar favoritos
    response = client.get("/api/favoritos")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_verificar_favorito(client: TestClient, usuario_data, cancion_data):
    """Probar verificación de si una canción es favorita"""
    # Crear usuario, canción y favorito
    user_response = client.post("/api/usuarios", json=usuario_data)
    song_response = client.post("/api/canciones", json=cancion_data)

    user_id = user_response.json()["id"]
    song_id = song_response.json()["id"]

    favorito_data = {"id_usuario": user_id, "id_cancion": song_id}
    client.post("/api/favoritos", json=favorito_data)

    # Verificar si es favorito
    response = client.get(f"/api/favoritos/verificar/{user_id}/{song_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["es_favorito"] is True


# ============================================================================
# PRUEBAS DE VALIDACIÓN
# ============================================================================


def test_validacion_usuario_email_invalido(client: TestClient):
    """Probar validación de email inválido"""
    invalid_data = {"nombre": "Usuario Test", "correo": "email-invalido"}

    response = client.post("/api/usuarios", json=invalid_data)
    assert response.status_code == 422


def test_validacion_cancion_duracion_invalida(client: TestClient):
    """Probar validación de duración inválida en canción"""
    invalid_data = {
        "titulo": "Canción Test",
        "artista": "Artista Test",
        "album": "Álbum Test",
        "duracion": -10,  # Duración negativa
        "año": 2023,
        "genero": "Rock",
    }

    response = client.post("/api/canciones", json=invalid_data)
    assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__])

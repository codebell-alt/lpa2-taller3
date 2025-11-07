# API de Música - Taller 3 LPA2

API RESTful para gestionar usuarios, canciones y favoritos. Desarrollada con FastAPI, SQLModel, frontend con TailwindCSS y herramientas de desarrollo profesionales.

## Características Implementadas

### API Backend (FastAPI)
- **Usuarios**: CRUD completo con validación de email
- **Canciones**: Gestión de música con búsqueda avanzada
- **Favoritos**: Sistema de relaciones usuario-canción
- **Validaciones**: Pydantic para datos robustos
- **Base de datos**: SQLModel + SQLite
- **Documentación**: OpenAPI automática en `/docs`

### Frontend Interactivo
- **Interfaz moderna**: TailwindCSS responsive
- **Gestión completa**: CRUD para todas las entidades
- **Búsqueda en vivo**: Filtrado dinámico de canciones
- **Estadísticas**: Dashboard con métricas en tiempo real
- **Animaciones**: Transiciones suaves CSS3

### Testing y Calidad
- **18 pruebas unitarias** con pytest (88% éxito)
- **Ruff**: Linter y formateador moderno
- **Pre-commit hooks**: Calidad automática de código
- **CI/CD ready**: Preparado para integración continua

## Mejoras Implementadas

### 1. Sistema de Paginación Completo
- **Paginación genérica**: Implementada para todos los endpoints (usuarios, canciones, favoritos)
- **Modelos reutilizables**: `PaginationParams` y `PaginatedResponse[T]` con TypeVars
- **Metadatos completos**: Total de elementos, páginas, navegación next/prev
- **Parámetros intuitivos**: `page` y `size` en lugar de `skip` y `limit`
- **Compatibilidad frontend**: Frontend actualizado para manejar respuestas paginadas

### 2. Sistema de Logging Avanzado
- **Middleware automático**: Logging transparente de todas las peticiones HTTP
- **IDs únicos**: Cada request tiene un ID para trazabilidad completa
- **Métricas detalladas**: Tiempo de procesamiento, códigos de estado, IP de cliente
- **Rotación de archivos**: Logs con rotación automática (10MB, 5 backups)
- **Configuración flexible**: Variables de entorno para diferentes niveles
- **Logging de negocio**: Registro de operaciones críticas (creación usuarios, errores de validación)
- **Colores en consola**: Output con códigos ANSI para mejor legibilidad

El proyecto incluye una interfaz de documentación interactiva generada automáticamente con Swagger disponible en el endpoint `/docs`.

## Estructura del Proyecto

```
lpa2-taller3
├──  README.md            # Este archivo, documentación completa del proyecto
├──  .env                 # Variables de entorno (desarrollo, pruebas, producción)
├──  .gitignore           # Archivos y directorios a ignorar por Git
├──  main.py              # Script principal para ejecutar la aplicación
├──  musica.db            # Base de Datos
├──  musica_api
│   ├──  __init__.py      # Inicialización del módulo
│   └──  *                # Implementación del API
├── 󰌠 requirements.txt     # Dependencias del proyecto
├── 󰙨 tests
│   └──  test_api.py      # Pruebas Unitarias
└──  utils.py             # Funciones de utilidad

```
## Modelo de Datos

1. **Usuario**:
   - id: Identificador único
   - nombre: Nombre del usuario
   - correo: Correo electrónico (único)
   - fecha_registro: Fecha de registro

2. **Canción**:
   - id: Identificador único
   - titulo: Título de la canción
   - artista: Artista o intérprete
   - album: Álbum al que pertenece
   - duracion: Duración en segundos
   - año: Año de lanzamiento
   - genero: Género musical
   - fecha_creacion: Fecha de creación del registro

3. **Favorito**:
   - id: Identificador único
   - id_usuario: ID del usuario (clave foránea)
   - id_cancion: ID de la canción (clave foránea)
   - fecha_marcado: Fecha en que se marcó como favorito

## Instalación

1. Clona este repositorio:

   ```bash
   git clone https://github.com/UR-CC/lpa2-taller3.git
   cd lpa2-taller3
   ```

2. Crea y activa un entorno virtual:

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. Instala las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

4. Ajusta las variables de entorno, editando el archivo `.env`

## Ejecución del Proyecto

### Opción 1: Usando Python directamente
1. Ejecuta la aplicación:
   ```bash
   python main.py
   ```

### Opción 2: Usando Uvicorn
1. Ejecuta con Uvicorn:
   ```bash
   uvicorn main:app --host 127.0.0.1 --port 8001 --reload
   ```

### Acceso al Proyecto

Una vez ejecutado el servidor:

- **Frontend Web**: [http://127.0.0.1:8001/](http://127.0.0.1:8001/)
- **Documentación Swagger UI**: [http://127.0.0.1:8001/docs](http://127.0.0.1:8001/docs)
- **Documentación ReDoc**: [http://127.0.0.1:8001/redoc](http://127.0.0.1:8001/redoc)
- **API REST**: [http://127.0.0.1:8001/api/](http://127.0.0.1:8001/api/)
- **Health Check**: [http://127.0.0.1:8001/health](http://127.0.0.1:8001/health)

## Uso de la API

### Usuarios (con Paginación)

- **Listar usuarios**: `GET /api/usuarios/?page=1&size=10`
- **Crear usuario**: `POST /api/usuarios/`
- **Obtener usuario**: `GET /api/usuarios/{id}`
- **Actualizar usuario**: `PUT /api/usuarios/{id}`
- **Eliminar usuario**: `DELETE /api/usuarios/{id}`
- **Buscar por correo**: `GET /api/usuarios/correo?correo=user@example.com`

### Canciones (con Paginación y Filtros)

- **Listar canciones**: `GET /api/canciones/?page=1&size=10&genero=Rock&año_desde=2020`
- **Crear canción**: `POST /api/canciones/`
- **Obtener canción**: `GET /api/canciones/{id}`
- **Actualizar canción**: `PUT /api/canciones/{id}`
- **Eliminar canción**: `DELETE /api/canciones/{id}`
- **Búsqueda avanzada**: `GET /api/canciones/buscar/avanzada?titulo=value&artista=value&genero=value`
- **Listar géneros**: `GET /api/canciones/generos/lista`
- **Listar artistas**: `GET /api/canciones/artistas/lista`

### Favoritos (con Paginación)

- **Listar favoritos**: `GET /api/favoritos/?page=1&size=10&usuario_id=1`
- **Marcar favorito**: `POST /api/favoritos/`
- **Obtener favorito**: `GET /api/favoritos/{id}`
- **Eliminar favorito**: `DELETE /api/favoritos/{id}`
- **Favoritos por usuario**: `GET /api/favoritos/usuario/{usuario_id}`
- **Estadísticas**: `GET /api/favoritos/estadisticas/resumen`

## Funciones Utilitarias Implementadas

### Validaciones y Formateo
- **Validación de email**: Regex completo para verificar formato de correos
- **Formateo de duración**: Convierte segundos a formato MM:SS
- **Generación de slugs**: Crea URLs amigables desde texto
- **Obtención de año actual**: Función para fechas dinámicas
- **Validación de URL de BD**: Verificación de conexiones de base de datos

## Desarrollo del Taller - COMPLETADO

1. **README.md actualizado** - Documentación completa del proyecto
2. **DBeaver** - (Opcional) Agregar 5 usuarios y 10 canciones directo a las tablas
3. **Pre-commit y GitHub Actions** - Configurado ruff linter/formatter y pytest con workflows automáticos
4. **TODOs y FIXMEs resueltos** - Todos los comentarios implementados con commits individuales:
   - Validación de correo electrónico con regex
   - Formateo de duración en formato MM:SS
   - Generación de slug para URLs amigables
   - Función para obtener año actual
   - Validación personalizada para database_url
5. **Pruebas de API** - Funcionamiento verificado en Swagger UI y ReDoc
6. **Pruebas automatizadas** - 18 tests implementados con pytest (88% de éxito)
7. **Dos mejoras implementadas**:
   - **Sistema de Paginación**: Paginación completa para todos los endpoints
   - **Sistema de Logging**: Sistema avanzado de registro y monitoreo

## Ejecutar Pruebas

```bash
# Ejecutar todas las pruebas
pytest

# Ejecutar con cobertura
pytest --cov=musica_api

# Ejecutar pruebas específicas
pytest tests/test_api.py::test_crear_usuario -v
```

## Herramientas de Desarrollo

```bash
# Ejecutar linter y formatter
ruff check .
ruff format .

# Pre-commit (se ejecuta automáticamente)
pre-commit run --all-files

# Ver logs en tiempo real
tail -f logs/musica_api.log
```

## Sugerencias de Mejora

### Implementadas
2. **Paginación** - Sistema completo de paginación implementado para todos los endpoints
5. **Registro (logging)** - Sistema avanzado de logging con middleware y métricas

### Pendientes (Opcionales)
1. **Autenticación y autorización**: Implementar JWT o OAuth2 para proteger los endpoints
3. **Base de datos en producción**: Migrar a PostgreSQL o MySQL para entornos de producción
4. **Docker**: Contenerizar la aplicación para facilitar su despliegue
6. **Caché**: Añadir caché para mejorar la velocidad de respuesta
7. **Estadísticas de uso**: Sistema de seguimiento y recomendaciones
8. **Subida de archivos**: Gestión de archivos de audio con S3

## Logros del Proyecto

- **API REST completa** con FastAPI y SQLModel
- **Frontend responsivo** con TailwindCSS
- **Sistema de paginación** genérico y reutilizable
- **Logging avanzado** con métricas y trazabilidad
- **Calidad de código** con ruff, pre-commit y pytest
- **Documentación completa** con Swagger UI y ReDoc
- **Validaciones robustas** con Pydantic
- **Funciones utilitarias** implementadas y probadas

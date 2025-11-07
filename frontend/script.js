/**
 * API de Música - Frontend JavaScript
 * Desarrollado por Isabella Ramírez Franco (@codebell-alt)
 *
 * Este archivo maneja toda la interacción con la API REST de música,
 * incluyendo CRUD de usuarios, canciones y favoritos.
 */

// Configuración de la API
const API_BASE_URL = 'http://127.0.0.1:8001';

// Estado global de la aplicación
let currentTab = 'usuarios';
let users = [];
let songs = [];
let favorites = [];
let genres = [];

// ============================================================================
// INICIALIZACIÓN Y UTILIDADES
// ============================================================================

// Inicializar la aplicación cuando se carga la página
document.addEventListener('DOMContentLoaded', function() {
    checkApiStatus();
    showTab('usuarios');
    loadUsers();
});

// Verificar el estado de la API
async function checkApiStatus() {
    const statusElement = document.getElementById('api-status');

    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();

        if (response.ok && data.status === 'healthy') {
            statusElement.innerHTML = `
                <div class="flex items-center">
                    <div class="h-3 w-3 bg-green-500 rounded-full mr-2"></div>
                    <span class="text-sm text-green-600 font-medium">API Conectada</span>
                </div>
            `;
        } else {
            throw new Error('API no saludable');
        }
    } catch (error) {
        statusElement.innerHTML = `
            <div class="flex items-center">
                <div class="h-3 w-3 bg-red-500 rounded-full mr-2"></div>
                <span class="text-sm text-red-600 font-medium">API Desconectada</span>
            </div>
        `;
        showToast('Error de conexión con la API', 'error');
    }
}

// Mostrar/ocultar tabs
function showTab(tabName) {
    // Resetear todos los tabs al estado inactivo
    document.querySelectorAll('.tab-button').forEach(button => {
        button.className = 'tab-button flex-1 py-6 px-6 font-semibold text-center transition-all duration-300 bg-gray-100 text-gray-600 hover:bg-gradient-purple hover:text-white relative overflow-hidden group';
    });

    // Configurar estilos específicos por tab
    const tabConfigs = {
        'usuarios': 'bg-gradient-pink text-white',
        'canciones': 'bg-gradient-purple text-white',
        'favoritos': 'bg-yellow-400 text-white',
        'estadisticas': 'bg-green-500 text-white'
    };

    // Aplicar clase activa al tab seleccionado
    const activeTab = document.getElementById(`tab-${tabName}`);
    const baseClasses = 'tab-button flex-1 py-6 px-6 font-semibold text-center transition-all duration-300 relative overflow-hidden group';
    const roundedClasses = tabName === 'usuarios' ? 'rounded-tl-2xl' :
                          tabName === 'estadisticas' ? 'rounded-tr-2xl' : '';

    activeTab.className = `${baseClasses} ${tabConfigs[tabName]} ${roundedClasses}`;

    // Mostrar/ocultar contenido con animación
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.add('hidden');
    });

    const activeContent = document.getElementById(`content-${tabName}`);
    activeContent.classList.remove('hidden');
    activeContent.classList.add('animate-scaleIn');

    currentTab = tabName;

    // Cargar datos específicos del tab
    switch(tabName) {
        case 'usuarios':
            loadUsers();
            break;
        case 'canciones':
            loadSongs();
            loadGenres();
            break;
        case 'favoritos':
            loadFavorites();
            loadUsersForSelect();
            break;
        case 'estadisticas':
            loadStatistics();
            break;
    }
}

// Mostrar notificaciones toast
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    const icon = document.getElementById('toast-icon');
    const messageEl = document.getElementById('toast-message');

    messageEl.textContent = message;

    // Configurar colores según el tipo
    if (type === 'error') {
        toast.className = 'fixed top-4 right-4 bg-red-500 text-white px-6 py-3 rounded-lg shadow-lg z-50';
        icon.className = 'fas fa-exclamation-circle mr-2';
    } else if (type === 'warning') {
        toast.className = 'fixed top-4 right-4 bg-yellow-500 text-white px-6 py-3 rounded-lg shadow-lg z-50';
        icon.className = 'fas fa-exclamation-triangle mr-2';
    } else {
        toast.className = 'fixed top-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg z-50';
        icon.className = 'fas fa-check-circle mr-2';
    }

    toast.classList.remove('hidden');

    // Ocultar después de 3 segundos
    setTimeout(() => {
        toast.classList.add('hidden');
    }, 3000);
}

// Funciones para modal
function showModal(title, content) {
    document.getElementById('modal-title').textContent = title;
    document.getElementById('modal-content').innerHTML = content;
    document.getElementById('modal').classList.remove('hidden');
}

function closeModal() {
    document.getElementById('modal').classList.add('hidden');
}

// Formatear fecha
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Formatear duración en segundos a MM:SS
function formatDuration(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
}

// ============================================================================
// GESTIÓN DE USUARIOS
// ============================================================================

// Cargar todos los usuarios
async function loadUsers() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/usuarios/`);
        const data = await response.json();

        if (response.ok) {
            // Ahora la API devuelve un objeto paginado con la propiedad 'items'
            users = data.items || data; // Soporte para ambos formatos
            renderUsers(users);
        } else {
            throw new Error(data.detail || 'Error al cargar usuarios');
        }
    } catch (error) {
        showToast(`Error al cargar usuarios: ${error.message}`, 'error');
    }
}

// Renderizar lista de usuarios con diseño moderno
function renderUsers(userList) {
    const container = document.getElementById('usuarios-list');

    if (userList.length === 0) {
        container.innerHTML = `
            <div class="col-span-full text-center py-16">
                <div class="animate-float mb-6">
                    <i class="fas fa-users text-gray-300 text-6xl"></i>
                </div>
                <h3 class="text-xl font-semibold text-gray-600 mb-2">No hay usuarios registrados</h3>
                <p class="text-gray-500">Comienza agregando tu primer usuario al sistema</p>
            </div>
        `;
        return;
    }

    container.innerHTML = userList.map(user => `
        <div class="music-card bg-white rounded-2xl p-6 hover:shadow-2xl transition-all duration-300 transform hover:scale-105 animate-slideInFromBottom">
            <div class="relative">
                <!-- Avatar y header -->
                <div class="flex items-center mb-4">
                    <div class="bg-gradient-to-r from-pink-400 to-purple-600 rounded-full p-3 mr-4">
                        <i class="fas fa-user text-white text-xl"></i>
                    </div>
                    <div class="flex-1">
                        <h4 class="font-bold text-gray-800 text-lg">${user.nombre}</h4>
                        <p class="text-gray-500 text-sm">ID: #${user.id.toString().padStart(3, '0')}</p>
                    </div>
                </div>

                <!-- Información del usuario -->
                <div class="space-y-3 mb-6">
                    <div class="flex items-center bg-gray-50 rounded-lg p-3">
                        <i class="fas fa-envelope text-music-primary mr-3"></i>
                        <span class="text-gray-700 text-sm">${user.correo}</span>
                    </div>
                    <div class="flex items-center bg-gray-50 rounded-lg p-3">
                        <i class="fas fa-calendar text-music-secondary mr-3"></i>
                        <span class="text-gray-700 text-sm">${formatDate(user.fecha_registro)}</span>
                    </div>
                </div>

                <!-- Acciones -->
                <div class="flex space-x-2">
                    <button onclick="editUser(${user.id})"
                            class="flex-1 bg-blue-500 hover:bg-blue-600 text-white py-3 px-4 rounded-xl font-semibold transition-all duration-300 transform hover:scale-105">
                        <i class="fas fa-edit mr-2"></i>Editar
                    </button>
                    <button onclick="deleteUser(${user.id}, '${user.nombre}')"
                            class="flex-1 bg-red-500 hover:bg-red-600 text-white py-3 px-4 rounded-xl font-semibold transition-all duration-300 transform hover:scale-105">
                        <i class="fas fa-trash mr-2"></i>Eliminar
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

// Buscar usuario por email (filtrado del lado cliente por ahora)
async function searchUserByEmail() {
    const email = document.getElementById('search-email').value.trim();

    if (!email) {
        showToast('Por favor ingresa un email para buscar', 'warning');
        return;
    }

    try {
        // Obtener todos los usuarios y filtrar del lado cliente
        const response = await fetch(`${API_BASE_URL}/api/usuarios/`);
        const data = await response.json();

        if (response.ok) {
            // Filtrar usuarios por email
            const usuarios = data.items || data;
            const usuariosEncontrados = usuarios.filter(usuario =>
                usuario.correo.toLowerCase().includes(email.toLowerCase())
            );

            if (usuariosEncontrados.length > 0) {
                renderUsers(usuariosEncontrados);
                showToast(`Se encontraron ${usuariosEncontrados.length} usuario(s)`, 'success');
            } else {
                renderUsers([]);
                showToast('No se encontraron usuarios con ese email', 'warning');
            }
        } else {
            throw new Error('Error al buscar usuarios');
        }
    } catch (error) {
        showToast(`Error en la búsqueda: ${error.message}`, 'error');
        console.error('Error al buscar usuarios:', error);
    }
}

// Mostrar formulario de creación de usuario
function showCreateUserForm() {
    const formContent = `
        <form id="user-form" onsubmit="createUser(event)">
            <div class="mb-4">
                <label class="block text-sm font-medium text-gray-700 mb-2">Nombre completo</label>
                <input type="text" id="user-nombre" required
                       class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-music-primary focus:border-transparent">
            </div>
            <div class="mb-6">
                <label class="block text-sm font-medium text-gray-700 mb-2">Email</label>
                <input type="email" id="user-email" required
                       class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-music-primary focus:border-transparent">
            </div>
            <div class="flex justify-end space-x-3">
                <button type="button" onclick="closeModal()"
                        class="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors">
                    Cancelar
                </button>
                <button type="submit"
                        class="bg-music-primary text-white px-6 py-2 rounded-lg hover:bg-purple-700 transition-colors">
                    Crear Usuario
                </button>
            </div>
        </form>
    `;

    showModal('Nuevo Usuario', formContent);
}

// Crear nuevo usuario
async function createUser(event) {
    event.preventDefault();

    const userData = {
        nombre: document.getElementById('user-nombre').value,
        correo: document.getElementById('user-email').value
    };

    try {
        const response = await fetch(`${API_BASE_URL}/api/usuarios/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(userData)
        });

        const data = await response.json();

        if (response.ok) {
            showToast('Usuario creado exitosamente');
            closeModal();
            loadUsers();
        } else {
            throw new Error(data.detail || 'Error al crear usuario');
        }
    } catch (error) {
        showToast(`Error: ${error.message}`, 'error');
    }
}

// Editar usuario
async function editUser(userId) {
    // Buscar el usuario en la lista actual
    const user = users.find(u => u.id === userId);
    if (!user) return;

    const formContent = `
        <form id="edit-user-form" onsubmit="updateUser(event, ${userId})">
            <div class="mb-4">
                <label class="block text-sm font-medium text-gray-700 mb-2">Nombre completo</label>
                <input type="text" id="edit-user-nombre" value="${user.nombre}" required
                       class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-music-primary focus:border-transparent">
            </div>
            <div class="mb-6">
                <label class="block text-sm font-medium text-gray-700 mb-2">Email</label>
                <input type="email" id="edit-user-email" value="${user.correo}" required
                       class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-music-primary focus:border-transparent">
            </div>
            <div class="flex justify-end space-x-3">
                <button type="button" onclick="closeModal()"
                        class="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors">
                    Cancelar
                </button>
                <button type="submit"
                        class="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors">
                    Actualizar Usuario
                </button>
            </div>
        </form>
    `;

    showModal('Editar Usuario', formContent);
}

// Actualizar usuario
async function updateUser(event, userId) {
    event.preventDefault();

    const userData = {
        nombre: document.getElementById('edit-user-nombre').value,
        correo: document.getElementById('edit-user-email').value
    };

    try {
        const response = await fetch(`${API_BASE_URL}/api/usuarios/${userId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(userData)
        });

        const data = await response.json();

        if (response.ok) {
            showToast('Usuario actualizado exitosamente');
            closeModal();
            loadUsers();
        } else {
            throw new Error(data.detail || 'Error al actualizar usuario');
        }
    } catch (error) {
        showToast(`Error: ${error.message}`, 'error');
    }
}

// Eliminar usuario
async function deleteUser(userId, userName) {
    if (!confirm(`¿Estás seguro de que quieres eliminar al usuario "${userName}"?`)) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/api/usuarios/${userId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            showToast('Usuario eliminado exitosamente');
            loadUsers();
        } else {
            const data = await response.json();
            throw new Error(data.detail || 'Error al eliminar usuario');
        }
    } catch (error) {
        showToast(`Error: ${error.message}`, 'error');
    }
}

// ============================================================================
// GESTIÓN DE CANCIONES
// ============================================================================

// Cargar todas las canciones
async function loadSongs() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/canciones/`);
        const data = await response.json();

        if (response.ok) {
            // Ahora la API devuelve un objeto paginado con la propiedad 'items'
            songs = data.items || data; // Soporte para ambos formatos
            renderSongs(songs);
        } else {
            throw new Error(data.detail || 'Error al cargar canciones');
        }
    } catch (error) {
        showToast(`Error al cargar canciones: ${error.message}`, 'error');
    }
}

// Cargar géneros para el select
async function loadGenres() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/canciones/generos/lista`);
        const data = await response.json();

        if (response.ok) {
            genres = data;
            const select = document.getElementById('search-genero');
            select.innerHTML = '<option value="">Todos los géneros</option>' +
                data.map(genre => `<option value="${genre}">${genre}</option>`).join('');
        }
    } catch (error) {
        console.error('Error al cargar géneros:', error);
    }
}

// Renderizar lista de canciones
function renderSongs(songList) {
    const container = document.getElementById('canciones-list');

    if (songList.length === 0) {
        container.innerHTML = `
            <div class="col-span-full text-center py-8">
                <i class="fas fa-music text-gray-300 text-4xl mb-4"></i>
                <p class="text-gray-500">No se encontraron canciones</p>
            </div>
        `;
        return;
    }

    container.innerHTML = songList.map(song => `
        <div class="bg-gradient-to-br from-white to-gray-50 rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow border">
            <div class="flex items-center mb-3">
                <div class="h-12 w-12 bg-gradient-to-br from-music-secondary to-music-primary rounded-lg flex items-center justify-center mr-3">
                    <i class="fas fa-play text-white"></i>
                </div>
                <div class="flex-1 min-w-0">
                    <h4 class="font-semibold text-gray-900 truncate">${song.titulo}</h4>
                    <p class="text-sm text-gray-600 truncate">${song.artista}</p>
                </div>
            </div>

            <div class="space-y-1 text-xs text-gray-500 mb-3">
                <p><i class="fas fa-compact-disc w-4"></i> ${song.album}</p>
                <p><i class="fas fa-tags w-4"></i> ${song.genero}</p>
                <p><i class="fas fa-clock w-4"></i> ${formatDuration(song.duracion)}</p>
                <p><i class="fas fa-calendar w-4"></i> ${song.año}</p>
            </div>

            <div class="flex justify-between items-center">
                <span class="text-xs text-gray-400">ID: ${song.id}</span>
                <div class="flex space-x-2">
                    <button onclick="editSong(${song.id})"
                            class="text-blue-600 hover:text-blue-800 transition-colors">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button onclick="deleteSong(${song.id}, '${song.titulo}')"
                            class="text-red-600 hover:text-red-800 transition-colors">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

// Buscar canciones con filtros
async function searchSongs() {
    const params = new URLSearchParams();

    const titulo = document.getElementById('search-titulo').value.trim();
    const artista = document.getElementById('search-artista').value.trim();
    const album = document.getElementById('search-album').value.trim();
    const genero = document.getElementById('search-genero').value;

    if (titulo) params.append('titulo', titulo);
    if (artista) params.append('artista', artista);
    if (album) params.append('album', album);
    if (genero) params.append('genero', genero);

    try {
        // Obtener todas las canciones y filtrar del lado cliente
        const response = await fetch(`${API_BASE_URL}/api/canciones/`);
        const data = await response.json();

        if (response.ok) {
            let canciones = data.items || data;

            // Aplicar filtros
            if (titulo) {
                canciones = canciones.filter(cancion =>
                    cancion.titulo.toLowerCase().includes(titulo.toLowerCase())
                );
            }
            if (artista) {
                canciones = canciones.filter(cancion =>
                    cancion.artista.toLowerCase().includes(artista.toLowerCase())
                );
            }
            if (album) {
                canciones = canciones.filter(cancion =>
                    cancion.album.toLowerCase().includes(album.toLowerCase())
                );
            }
            if (genero) {
                canciones = canciones.filter(cancion =>
                    cancion.genero.toLowerCase().includes(genero.toLowerCase())
                );
            }

            renderSongs(canciones);
            if (canciones.length === 0) {
                showToast('No se encontraron canciones con esos filtros', 'warning');
            } else {
                showToast(`Se encontraron ${canciones.length} canción(es)`, 'success');
            }
        } else {
            throw new Error('Error al buscar canciones');
        }
    } catch (error) {
        showToast(`Error en la búsqueda: ${error.message}`, 'error');
        console.error('Error al buscar canciones:', error);
    }
}

// Mostrar formulario de creación de canción
function showCreateSongForm() {
    const formContent = `
        <form id="song-form" onsubmit="createSong(event)">
            <div class="grid grid-cols-2 gap-4 mb-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Título</label>
                    <input type="text" id="song-titulo" required
                           class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-music-secondary focus:border-transparent">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Artista</label>
                    <input type="text" id="song-artista" required
                           class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-music-secondary focus:border-transparent">
                </div>
            </div>
            <div class="grid grid-cols-2 gap-4 mb-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Álbum</label>
                    <input type="text" id="song-album" required
                           class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-music-secondary focus:border-transparent">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Género</label>
                    <input type="text" id="song-genero" required
                           class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-music-secondary focus:border-transparent">
                </div>
            </div>
            <div class="grid grid-cols-2 gap-4 mb-6">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Duración (segundos)</label>
                    <input type="number" id="song-duracion" min="1" max="3600" required
                           class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-music-secondary focus:border-transparent">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Año</label>
                    <input type="number" id="song-año" min="1900" max="2030" required
                           class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-music-secondary focus:border-transparent">
                </div>
            </div>
            <div class="flex justify-end space-x-3">
                <button type="button" onclick="closeModal()"
                        class="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors">
                    Cancelar
                </button>
                <button type="submit"
                        class="bg-music-secondary text-white px-6 py-2 rounded-lg hover:bg-pink-600 transition-colors">
                    Crear Canción
                </button>
            </div>
        </form>
    `;

    showModal('Nueva Canción', formContent);
}

// Crear nueva canción
async function createSong(event) {
    event.preventDefault();

    const songData = {
        titulo: document.getElementById('song-titulo').value,
        artista: document.getElementById('song-artista').value,
        album: document.getElementById('song-album').value,
        genero: document.getElementById('song-genero').value,
        duracion: parseInt(document.getElementById('song-duracion').value),
        año: parseInt(document.getElementById('song-año').value)
    };

    try {
        const response = await fetch(`${API_BASE_URL}/api/canciones`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(songData)
        });

        const data = await response.json();

        if (response.ok) {
            showToast('Canción creada exitosamente');
            closeModal();
            loadSongs();
        } else {
            throw new Error(data.detail || 'Error al crear canción');
        }
    } catch (error) {
        showToast(`Error: ${error.message}`, 'error');
    }
}

// Editar canción (similar a editUser pero para canciones)
async function editSong(songId) {
    const song = songs.find(s => s.id === songId);
    if (!song) return;

    const formContent = `
        <form id="edit-song-form" onsubmit="updateSong(event, ${songId})">
            <div class="grid grid-cols-2 gap-4 mb-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Título</label>
                    <input type="text" id="edit-song-titulo" value="${song.titulo}" required
                           class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-music-secondary focus:border-transparent">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Artista</label>
                    <input type="text" id="edit-song-artista" value="${song.artista}" required
                           class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-music-secondary focus:border-transparent">
                </div>
            </div>
            <div class="grid grid-cols-2 gap-4 mb-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Álbum</label>
                    <input type="text" id="edit-song-album" value="${song.album}" required
                           class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-music-secondary focus:border-transparent">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Género</label>
                    <input type="text" id="edit-song-genero" value="${song.genero}" required
                           class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-music-secondary focus:border-transparent">
                </div>
            </div>
            <div class="grid grid-cols-2 gap-4 mb-6">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Duración (segundos)</label>
                    <input type="number" id="edit-song-duracion" value="${song.duracion}" min="1" max="3600" required
                           class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-music-secondary focus:border-transparent">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Año</label>
                    <input type="number" id="edit-song-año" value="${song.año}" min="1900" max="2030" required
                           class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-music-secondary focus:border-transparent">
                </div>
            </div>
            <div class="flex justify-end space-x-3">
                <button type="button" onclick="closeModal()"
                        class="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors">
                    Cancelar
                </button>
                <button type="submit"
                        class="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors">
                    Actualizar Canción
                </button>
            </div>
        </form>
    `;

    showModal('Editar Canción', formContent);
}

// Actualizar canción
async function updateSong(event, songId) {
    event.preventDefault();

    const songData = {
        titulo: document.getElementById('edit-song-titulo').value,
        artista: document.getElementById('edit-song-artista').value,
        album: document.getElementById('edit-song-album').value,
        genero: document.getElementById('edit-song-genero').value,
        duracion: parseInt(document.getElementById('edit-song-duracion').value),
        año: parseInt(document.getElementById('edit-song-año').value)
    };

    try {
        const response = await fetch(`${API_BASE_URL}/api/canciones/${songId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(songData)
        });

        const data = await response.json();

        if (response.ok) {
            showToast('Canción actualizada exitosamente');
            closeModal();
            loadSongs();
        } else {
            throw new Error(data.detail || 'Error al actualizar canción');
        }
    } catch (error) {
        showToast(`Error: ${error.message}`, 'error');
    }
}

// Eliminar canción
async function deleteSong(songId, songTitle) {
    if (!confirm(`¿Estás seguro de que quieres eliminar la canción "${songTitle}"?`)) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/api/canciones/${songId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            showToast('Canción eliminada exitosamente');
            loadSongs();
        } else {
            const data = await response.json();
            throw new Error(data.detail || 'Error al eliminar canción');
        }
    } catch (error) {
        showToast(`Error: ${error.message}`, 'error');
    }
}

// ============================================================================
// GESTIÓN DE FAVORITOS
// ============================================================================

// Cargar todos los favoritos
async function loadFavorites() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/favoritos/`);
        const data = await response.json();

        if (response.ok) {
            // Ahora la API devuelve un objeto paginado con la propiedad 'items'
            favorites = data.items || data; // Soporte para ambos formatos
            renderFavorites(favorites);
        } else {
            throw new Error(data.detail || 'Error al cargar favoritos');
        }
    } catch (error) {
        showToast(`Error al cargar favoritos: ${error.message}`, 'error');
    }
}

// Cargar usuarios para el selector
async function loadUsersForSelect() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/usuarios/`);
        const data = await response.json();

        if (response.ok) {
            const userList = data.items || data; // Soporte para formato paginado
            const select = document.getElementById('filter-usuario');
            select.innerHTML = '<option value="">Todos los usuarios</option>' +
                userList.map(user => `<option value="${user.id}">${user.nombre} (${user.correo})</option>`).join('');
        }
    } catch (error) {
        console.error('Error al cargar usuarios:', error);
    }
}

// Renderizar lista de favoritos
function renderFavorites(favoritesList) {
    const container = document.getElementById('favoritos-list');

    if (favoritesList.length === 0) {
        container.innerHTML = `
            <div class="text-center py-8">
                <i class="fas fa-star text-gray-300 text-4xl mb-4"></i>
                <p class="text-gray-500">No se encontraron favoritos</p>
            </div>
        `;
        return;
    }

    container.innerHTML = favoritesList.map(favorite => `
        <div class="bg-gradient-to-r from-yellow-50 to-orange-50 rounded-lg p-4 border border-yellow-200 hover:shadow-md transition-shadow">
            <div class="flex justify-between items-start">
                <div class="flex-1">
                    <div class="flex items-center mb-2">
                        <i class="fas fa-star text-yellow-500 mr-2"></i>
                        <h4 class="font-semibold text-gray-900">${favorite.cancion.titulo}</h4>
                    </div>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                        <div>
                            <p class="text-gray-600 mb-1">
                                <i class="fas fa-user text-blue-500 mr-2"></i><strong>Usuario:</strong> ${favorite.usuario.nombre}
                            </p>
                            <p class="text-gray-600 mb-1">
                                <i class="fas fa-envelope text-gray-500 mr-2"></i>${favorite.usuario.correo}
                            </p>
                        </div>
                        <div>
                            <p class="text-gray-600 mb-1">
                                <i class="fas fa-microphone text-pink-500 mr-2"></i><strong>Artista:</strong> ${favorite.cancion.artista}
                            </p>
                            <p class="text-gray-600 mb-1">
                                <i class="fas fa-compact-disc text-purple-500 mr-2"></i><strong>Álbum:</strong> ${favorite.cancion.album}
                            </p>
                        </div>
                    </div>
                    <p class="text-gray-500 text-xs mt-2">
                        <i class="fas fa-calendar mr-2"></i>Marcado como favorito: ${formatDate(favorite.fecha_marcado)}
                    </p>
                </div>
                <div class="flex space-x-2 ml-4">
                    <button onclick="removeFavorite(${favorite.id})"
                            class="text-red-600 hover:text-red-800 transition-colors">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

// Filtrar favoritos por usuario
async function loadFavoritesByUser() {
    const userId = document.getElementById('filter-usuario').value;

    if (!userId) {
        loadFavorites();
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/api/favoritos/usuario/${userId}`);
        const data = await response.json();

        if (response.ok) {
            // Transformar la respuesta para que coincida con el formato esperado
            const favoritesWithDetails = data.map(cancion => ({
                id: null, // No tenemos el ID del favorito en esta respuesta
                cancion: cancion,
                usuario: users.find(u => u.id === parseInt(userId)) || { nombre: 'Usuario', correo: 'N/A' },
                fecha_marcado: new Date().toISOString()
            }));
            renderFavorites(favoritesWithDetails);
        } else {
            throw new Error(data.detail || 'Error al filtrar favoritos');
        }
    } catch (error) {
        showToast(`Error: ${error.message}`, 'error');
    }
}

// Mostrar formulario para agregar favorito
function showAddFavoriteForm() {
    // Primero cargar usuarios y canciones para los selects
    Promise.all([
        fetch(`${API_BASE_URL}/api/usuarios`).then(r => r.json()),
        fetch(`${API_BASE_URL}/api/canciones`).then(r => r.json())
    ]).then(([usersData, songsData]) => {
        const formContent = `
            <form id="favorite-form" onsubmit="addFavorite(event)">
                <div class="mb-4">
                    <label class="block text-sm font-medium text-gray-700 mb-2">Usuario</label>
                    <select id="favorite-usuario" required
                            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500 focus:border-transparent">
                        <option value="">Selecciona un usuario</option>
                        ${usersData.map(user => `<option value="${user.id}">${user.nombre} (${user.correo})</option>`).join('')}
                    </select>
                </div>
                <div class="mb-6">
                    <label class="block text-sm font-medium text-gray-700 mb-2">Canción</label>
                    <select id="favorite-cancion" required
                            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500 focus:border-transparent">
                        <option value="">Selecciona una canción</option>
                        ${songsData.map(song => `<option value="${song.id}">${song.titulo} - ${song.artista}</option>`).join('')}
                    </select>
                </div>
                <div class="flex justify-end space-x-3">
                    <button type="button" onclick="closeModal()"
                            class="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors">
                        Cancelar
                    </button>
                    <button type="submit"
                            class="bg-yellow-500 text-white px-6 py-2 rounded-lg hover:bg-yellow-600 transition-colors">
                        Agregar a Favoritos
                    </button>
                </div>
            </form>
        `;

        showModal('Agregar Favorito', formContent);
    }).catch(error => {
        showToast('Error al cargar datos para el formulario', 'error');
    });
}

// Agregar favorito
async function addFavorite(event) {
    event.preventDefault();

    const favoriteData = {
        id_usuario: parseInt(document.getElementById('favorite-usuario').value),
        id_cancion: parseInt(document.getElementById('favorite-cancion').value)
    };

    try {
        const response = await fetch(`${API_BASE_URL}/api/favoritos`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(favoriteData)
        });

        const data = await response.json();

        if (response.ok) {
            showToast('Canción agregada a favoritos exitosamente');
            closeModal();
            loadFavorites();
        } else {
            throw new Error(data.detail || 'Error al agregar favorito');
        }
    } catch (error) {
        showToast(`Error: ${error.message}`, 'error');
    }
}

// Eliminar favorito
async function removeFavorite(favoriteId) {
    if (!confirm('¿Estás seguro de que quieres quitar esta canción de favoritos?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/api/favoritos/${favoriteId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            showToast('Canción eliminada de favoritos');
            loadFavorites();
        } else {
            const data = await response.json();
            throw new Error(data.detail || 'Error al eliminar favorito');
        }
    } catch (error) {
        showToast(`Error: ${error.message}`, 'error');
    }
}

// ============================================================================
// ESTADÍSTICAS
// ============================================================================

// Cargar estadísticas
async function loadStatistics() {
    const container = document.getElementById('estadisticas-content');

    try {
        // Cargar estadísticas de múltiples endpoints
        const [statsResponse, favoritesStatsResponse, healthResponse] = await Promise.all([
            fetch(`${API_BASE_URL}/stats`),
            fetch(`${API_BASE_URL}/api/favoritos/estadisticas/resumen`),
            fetch(`${API_BASE_URL}/health`)
        ]);

        const [stats, favoritesStats, health] = await Promise.all([
            statsResponse.json(),
            favoritesStatsResponse.json(),
            healthResponse.json()
        ]);

        container.innerHTML = `
            <!-- Estadísticas generales -->
            <div class="bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-lg p-6">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-blue-100 text-sm">Total Usuarios</p>
                        <p class="text-3xl font-bold">${stats.estadisticas?.total_usuarios || 0}</p>
                    </div>
                    <i class="fas fa-users text-4xl text-blue-200"></i>
                </div>
            </div>

            <div class="bg-gradient-to-br from-pink-500 to-pink-600 text-white rounded-lg p-6">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-pink-100 text-sm">Total Canciones</p>
                        <p class="text-3xl font-bold">${stats.estadisticas?.total_canciones || 0}</p>
                    </div>
                    <i class="fas fa-music text-4xl text-pink-200"></i>
                </div>
            </div>

            <div class="bg-gradient-to-br from-yellow-500 to-yellow-600 text-white rounded-lg p-6">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-yellow-100 text-sm">Total Favoritos</p>
                        <p class="text-3xl font-bold">${favoritesStats.total_favoritos || 0}</p>
                    </div>
                    <i class="fas fa-star text-4xl text-yellow-200"></i>
                </div>
            </div>

            <!-- Estado del sistema -->
            <div class="bg-gradient-to-br from-green-500 to-green-600 text-white rounded-lg p-6">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-green-100 text-sm">Estado API</p>
                        <p class="text-lg font-semibold">${health.status === 'healthy' ? 'Saludable' : 'Con problemas'}</p>
                    </div>
                    <i class="fas fa-heartbeat text-4xl text-green-200"></i>
                </div>
            </div>

            <!-- Uptime del sistema -->
            <div class="bg-gradient-to-br from-purple-500 to-purple-600 text-white rounded-lg p-6">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-purple-100 text-sm">Uptime</p>
                        <p class="text-lg font-semibold">${Math.floor(health.uptime_seconds / 3600)}h ${Math.floor((health.uptime_seconds % 3600) / 60)}m</p>
                    </div>
                    <i class="fas fa-clock text-4xl text-purple-200"></i>
                </div>
            </div>

            <!-- Información de la aplicación -->
            <div class="bg-gradient-to-br from-gray-500 to-gray-600 text-white rounded-lg p-6">
                <div>
                    <p class="text-gray-100 text-sm mb-2">Versión API</p>
                    <p class="text-lg font-semibold mb-3">${health.version || 'N/A'}</p>
                    <div class="text-sm text-gray-200">
                        <p><i class="fas fa-server mr-2"></i>Puerto: ${health.port}</p>
                        <p><i class="fas fa-cog mr-2"></i>Entorno: ${health.environment}</p>
                    </div>
                </div>
            </div>
        `;

    } catch (error) {
        container.innerHTML = `
            <div class="col-span-full text-center py-8">
                <i class="fas fa-exclamation-triangle text-red-500 text-4xl mb-4"></i>
                <p class="text-gray-500">Error al cargar estadísticas</p>
                <p class="text-sm text-gray-400">${error.message}</p>
            </div>
        `;
    }
}

/**
 * Cliente API para FocusIT
 * Ejemplo de cómo consumir la API REST desde JavaScript
 * 
 * Uso:
 * import { API } from './api-client.js';
 * 
 * const result = await API.auth.login('usuario@example.com');
 * if (result.success) {
 *   console.log('Usuario:', result.data.user);
 * }
 */

const BASE_URL = '/api';

/**
 * Función auxiliar para hacer peticiones HTTP
 */
async function request(endpoint, options = {}) {
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    },
    credentials: 'include', // Importante para cookies de sesión
    ...options
  };

  try {
    const response = await fetch(`${BASE_URL}${endpoint}`, config);
    const data = await response.json();
    
    return data;
  } catch (error) {
    return {
      success: false,
      data: null,
      error: {
        code: 'NETWORK_ERROR',
        message: 'Error de conexión con el servidor'
      }
    };
  }
}

/**
 * API Client
 */
export const API = {
  /**
   * Autenticación
   */
  auth: {
    /**
     * Iniciar sesión
     * @param {string} email - Email del usuario
     * @returns {Promise<Object>}
     */
    login: async (email) => {
      return request('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email })
      });
    },

    /**
     * Cerrar sesión
     * @returns {Promise<Object>}
     */
    logout: async () => {
      return request('/auth/logout', {
        method: 'POST'
      });
    },

    /**
     * Registrar nuevo usuario
     * @param {Object} userData - Datos del usuario
     * @returns {Promise<Object>}
     */
    register: async (userData) => {
      return request('/auth/register', {
        method: 'POST',
        body: JSON.stringify(userData)
      });
    },

    /**
     * Obtener usuario actual
     * @returns {Promise<Object>}
     */
    me: async () => {
      return request('/auth/me');
    },

    /**
     * Verificar si hay sesión activa
     * @returns {Promise<Object>}
     */
    check: async () => {
      return request('/auth/check');
    }
  },

  /**
   * Tickets
   */
  tickets: {
    /**
     * Listar tickets
     * @param {Object} params - Parámetros de filtrado
     * @returns {Promise<Object>}
     */
    list: async (params = {}) => {
      const queryString = new URLSearchParams(params).toString();
      return request(`/tickets?${queryString}`);
    },

    /**
     * Obtener detalle de un ticket
     * @param {number} id - ID del ticket
     * @returns {Promise<Object>}
     */
    get: async (id) => {
      return request(`/tickets/${id}`);
    },

    /**
     * Crear nuevo ticket
     * @param {Object} ticketData - Datos del ticket
     * @returns {Promise<Object>}
     */
    create: async (ticketData) => {
      return request('/tickets', {
        method: 'POST',
        body: JSON.stringify(ticketData)
      });
    },

    /**
     * Agregar comentario a un ticket
     * @param {number} id - ID del ticket
     * @param {string} contenido - Contenido del comentario
     * @param {boolean} esInterno - Si es comentario interno
     * @returns {Promise<Object>}
     */
    addComment: async (id, contenido, esInterno = false) => {
      return request(`/tickets/${id}/comentarios`, {
        method: 'POST',
        body: JSON.stringify({ contenido, es_interno: esInterno })
      });
    },

    /**
     * Actualizar estado de un ticket (solo técnicos)
     * @param {number} id - ID del ticket
     * @param {string} estado - Nuevo estado
     * @param {number} tecnicoId - ID del técnico (opcional)
     * @returns {Promise<Object>}
     */
    updateStatus: async (id, estado, tecnicoId = null) => {
      const body = { estado };
      if (tecnicoId) body.tecnico_id = tecnicoId;
      
      return request(`/tickets/${id}/estado`, {
        method: 'PATCH',
        body: JSON.stringify(body)
      });
    },

    /**
     * Buscar artículos relacionados
     * @param {string} query - Término de búsqueda
     * @param {string} categoria - Categoría (opcional)
     * @returns {Promise<Object>}
     */
    searchArticles: async (query, categoria = '') => {
      const params = new URLSearchParams({ q: query, categoria });
      return request(`/tickets/buscar-articulos?${params}`);
    },

    /**
     * Obtener estadísticas (solo técnicos)
     * @param {string} categoria - Categoría (opcional)
     * @returns {Promise<Object>}
     */
    stats: async (categoria = '') => {
      const params = categoria ? `?categoria=${categoria}` : '';
      return request(`/tickets/estadisticas${params}`);
    }
  },

  /**
   * Base de Conocimiento
   */
  knowledge: {
    /**
     * Listar artículos
     * @param {Object} params - Parámetros de filtrado
     * @returns {Promise<Object>}
     */
    list: async (params = {}) => {
      const queryString = new URLSearchParams(params).toString();
      return request(`/knowledge?${queryString}`);
    },

    /**
     * Obtener artículo específico
     * @param {number} id - ID del artículo
     * @returns {Promise<Object>}
     */
    get: async (id) => {
      return request(`/knowledge/${id}`);
    },

    /**
     * Crear artículo (solo técnicos)
     * @param {Object} articleData - Datos del artículo
     * @returns {Promise<Object>}
     */
    create: async (articleData) => {
      return request('/knowledge', {
        method: 'POST',
        body: JSON.stringify(articleData)
      });
    },

    /**
     * Editar artículo (solo autor)
     * @param {number} id - ID del artículo
     * @param {Object} articleData - Datos actualizados
     * @returns {Promise<Object>}
     */
    update: async (id, articleData) => {
      return request(`/knowledge/${id}`, {
        method: 'PUT',
        body: JSON.stringify(articleData)
      });
    },

    /**
     * Eliminar artículo (solo autor)
     * @param {number} id - ID del artículo
     * @returns {Promise<Object>}
     */
    delete: async (id) => {
      return request(`/knowledge/${id}`, {
        method: 'DELETE'
      });
    },

    /**
     * Buscar sugerencias (autocompletado)
     * @param {string} query - Término de búsqueda
     * @returns {Promise<Object>}
     */
    suggestions: async (query) => {
      return request(`/knowledge/buscar-sugerencias?q=${query}`);
    },

    /**
     * Obtener estadísticas (solo técnicos)
     * @returns {Promise<Object>}
     */
    stats: async () => {
      return request('/knowledge/estadisticas');
    }
  },

  /**
   * Dashboard
   */
  dashboard: {
    /**
     * Obtener datos del dashboard principal
     * @returns {Promise<Object>}
     */
    home: async () => {
      return request('/dashboard/home');
    },

    /**
     * Buscar ayuda
     * @param {string} query - Término de búsqueda
     * @returns {Promise<Object>}
     */
    searchHelp: async (query) => {
      return request(`/dashboard/buscar-ayuda?q=${query}`);
    },

    /**
     * Obtener accesos rápidos
     * @returns {Promise<Object>}
     */
    quickAccess: async () => {
      return request('/dashboard/accesos-rapidos');
    },

    /**
     * Obtener estadísticas generales (solo técnicos)
     * @returns {Promise<Object>}
     */
    stats: async () => {
      return request('/dashboard/estadisticas');
    },

    /**
     * Obtener notificaciones (solo técnicos)
     * @returns {Promise<Object>}
     */
    notifications: async () => {
      return request('/dashboard/notificaciones');
    }
  },

  /**
   * Chatbot
   */
  chatbot: {
    /**
     * Enviar mensaje al chatbot
     * @param {string} mensaje - Mensaje del usuario
     * @param {string} telefono - Número de teléfono (opcional)
     * @returns {Promise<Object>}
     */
    sendMessage: async (mensaje, telefono = null) => {
      const body = { mensaje };
      if (telefono) body.telefono = telefono;
      
      return request('/chatbot/mensaje', {
        method: 'POST',
        body: JSON.stringify(body)
      });
    },

    /**
     * Obtener sesión activa
     * @param {string} telefono - Número de teléfono (opcional)
     * @returns {Promise<Object>}
     */
    getSession: async (telefono = null) => {
      const params = telefono ? `?telefono=${telefono}` : '';
      return request(`/chatbot/sesion${params}`);
    },

    /**
     * Reiniciar sesión
     * @param {string} telefono - Número de teléfono (opcional)
     * @returns {Promise<Object>}
     */
    resetSession: async (telefono = null) => {
      const params = telefono ? `?telefono=${telefono}` : '';
      return request(`/chatbot/sesion${params}`, {
        method: 'DELETE'
      });
    }
  }
};

/**
 * Utilidades para manejo de estados de carga
 */
export class LoadingState {
  constructor() {
    this.loading = false;
    this.error = null;
    this.data = null;
  }

  setLoading(loading) {
    this.loading = loading;
    if (loading) {
      this.error = null;
    }
  }

  setError(error) {
    this.error = error;
    this.loading = false;
  }

  setData(data) {
    this.data = data;
    this.loading = false;
    this.error = null;
  }
}

/**
 * Hook para manejo de estados (estilo React)
 */
export function useAPI(apiCall) {
  const state = new LoadingState();

  const execute = async (...args) => {
    state.setLoading(true);

    try {
      const result = await apiCall(...args);

      if (result.success) {
        state.setData(result.data);
      } else {
        state.setError(result.error.message);
      }

      return result;
    } catch (error) {
      state.setError('Error inesperado');
      return {
        success: false,
        error: { message: 'Error inesperado' }
      };
    }
  };

  return { state, execute };
}

/**
 * Ejemplo de uso:
 * 
 * // Login
 * const result = await API.auth.login('usuario@example.com');
 * if (result.success) {
 *   console.log('Bienvenido:', result.data.user.nombre);
 * } else {
 *   console.error('Error:', result.error.message);
 * }
 * 
 * // Crear ticket con loading state
 * const { state, execute } = useAPI(API.tickets.create);
 * 
 * const handleSubmit = async (ticketData) => {
 *   const result = await execute(ticketData);
 *   
 *   if (result.success) {
 *     showSuccessMessage(result.meta.message);
 *   } else {
 *     showErrorMessage(result.error.message);
 *   }
 * };
 * 
 * // Listar tickets con paginación
 * const tickets = await API.tickets.list({ page: 1, estado: 'nuevo' });
 * console.log('Tickets:', tickets.data.tickets);
 * console.log('Paginación:', tickets.meta.pagination);
 */

// Sistema de notificaciones avanzado para FocusIT
class NotificationManager {
    constructor() {
        this.enabled = false;
        this.soundEnabled = true;
        this.pushEnabled = false;
        this.previousNotifications = [];
        this.settings = this.loadSettings();
        this.init();
    }
    
    init() {
        // Solicitar permisos al cargar
        this.requestPermissions();
        
        // Cargar configuración del localStorage
        this.applySettings();
        
        // Crear panel de configuración
        this.createSettingsPanel();
    }
    
    loadSettings() {
        const defaultSettings = {
            soundEnabled: true,
            pushEnabled: true,
            criticalOnly: false,
            soundVolume: 0.5,
            autoRefreshInterval: 30000
        };
        
        const saved = localStorage.getItem('focusit_notification_settings');
        return saved ? { ...defaultSettings, ...JSON.parse(saved) } : defaultSettings;
    }
    
    saveSettings() {
        localStorage.setItem('focusit_notification_settings', JSON.stringify(this.settings));
    }
    
    applySettings() {
        this.soundEnabled = this.settings.soundEnabled;
        this.pushEnabled = this.settings.pushEnabled;
    }
    
    async requestPermissions() {
        if ('Notification' in window) {
            if (Notification.permission === 'default') {
                const permission = await Notification.requestPermission();
                this.pushEnabled = permission === 'granted';
                if (this.pushEnabled) {
                    this.showToast('✅ Notificaciones del navegador activadas', 'success');
                }
            } else {
                this.pushEnabled = Notification.permission === 'granted';
            }
        }
    }
    
    createSettingsPanel() {
        // Agregar botón de configuración al dropdown de notificaciones
        const menu = document.getElementById('notificationsMenu');
        if (menu) {
            // Se agregará dinámicamente cuando se carguen las notificaciones
        }
    }
    
    playSound(type = 'normal') {
        if (!this.soundEnabled) return;
        
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const volume = this.settings.soundVolume;
            
            if (type === 'critical') {
                // Sonido de alerta crítica: 3 tonos urgentes
                this.playTone(audioContext, 880, volume, 0.15); // A5
                setTimeout(() => this.playTone(audioContext, 1108, volume, 0.15), 200); // C#6
                setTimeout(() => this.playTone(audioContext, 880, volume, 0.15), 400); // A5
            } else if (type === 'urgent') {
                // Sonido de alta prioridad: 2 tonos
                this.playTone(audioContext, 659, volume * 0.8, 0.2); // E5
                setTimeout(() => this.playTone(audioContext, 784, volume * 0.8, 0.2), 250); // G5
            } else {
                // Sonido normal: tono suave
                this.playTone(audioContext, 523, volume * 0.6, 0.25); // C5
                setTimeout(() => this.playTone(audioContext, 659, volume * 0.6, 0.15), 150); // E5
            }
        } catch (error) {
            console.log('Audio no disponible:', error);
        }
    }
    
    playTone(audioContext, frequency, volume, duration) {
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.value = frequency;
        oscillator.type = 'sine';
        
        // Envelope para sonido más suave
        gainNode.gain.setValueAtTime(0, audioContext.currentTime);
        gainNode.gain.linearRampToValueAtTime(volume, audioContext.currentTime + 0.02);
        gainNode.gain.exponentialRampToValueAtTime(0.001, audioContext.currentTime + duration);
        
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + duration);
    }
    
    showPushNotification(title, message, priority = 'normal', url = null) {
        if (!this.pushEnabled || !('Notification' in window)) return;
        
        const icons = {
            'critical': '🚨',
            'high': '⚠️',
            'normal': '🔔',
            'low': 'ℹ️'
        };
        
        const notification = new Notification(title, {
            body: message,
            icon: '/static/favicon.ico',
            badge: '/static/favicon.ico',
            tag: `focusit-${priority}`,
            requireInteraction: priority === 'critical',
            silent: false,
            actions: url ? [
                { action: 'view', title: '👁️ Ver Ticket' },
                { action: 'dismiss', title: '✖️ Descartar' }
            ] : []
        });
        
        notification.onclick = () => {
            window.focus();
            if (url) window.location.href = url;
            notification.close();
        };
        
        // Auto-cerrar según prioridad
        const timeout = priority === 'critical' ? 15000 : 8000;
        setTimeout(() => notification.close(), timeout);
        
        return notification;
    }
    
    showToast(message, type = 'info', duration = 5000) {
        const container = this.getToastContainer();
        const toastId = `toast_${Date.now()}`;
        
        const icons = {
            'success': 'bi-check-circle-fill',
            'warning': 'bi-exclamation-triangle-fill',
            'danger': 'bi-exclamation-octagon-fill',
            'info': 'bi-info-circle-fill'
        };
        
        const toast = document.createElement('div');
        toast.id = toastId;
        toast.className = `toast align-items-center text-white bg-${type}`;
        toast.setAttribute('role', 'alert');
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="bi ${icons[type]} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        container.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast, { delay: duration });
        bsToast.show();
        
        toast.addEventListener('hidden.bs.toast', () => toast.remove());
    }
    
    getToastContainer() {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            container.style.zIndex = '1060';
            document.body.appendChild(container);
        }
        return container;
    }
    
    processNotifications(data) {
        if (!data.notificaciones || data.notificaciones.length === 0) {
            this.updateBadge(0);
            this.updateMenu([]);
            return;
        }
        
        // Detectar nuevas notificaciones
        const newNotifications = data.notificaciones.filter(notif => 
            !this.previousNotifications.some(prev => 
                prev.titulo === notif.titulo && prev.tiempo === notif.tiempo
            )
        );
        
        // Procesar solo si hay notificaciones nuevas
        if (newNotifications.length > 0) {
            newNotifications.forEach(notif => this.handleNewNotification(notif));
            this.previousNotifications = [...data.notificaciones];
        }
        
        // Actualizar UI
        this.updateBadge(data.notificaciones.length);
        this.updateMenu(data.notificaciones, data);
    }
    
    handleNewNotification(notification) {
        const priority = this.getPriorityLevel(notification.prioridad);
        
        // Filtrar por configuración
        if (this.settings.criticalOnly && priority !== 'critical') {
            return;
        }
        
        // Reproducir sonido
        this.playSound(priority);
        
        // Mostrar notificación push
        this.showPushNotification(
            notification.titulo,
            notification.mensaje,
            priority,
            notification.url
        );
        
        // Mostrar toast interno
        const toastType = priority === 'critical' ? 'danger' : 
                         priority === 'high' ? 'warning' : 'info';
        
        this.showToast(
            `${notification.titulo}: ${notification.mensaje}`,
            toastType,
            priority === 'critical' ? 8000 : 5000
        );
        
        // Efectos visuales especiales para críticos
        if (priority === 'critical') {
            this.flashNotificationIcon();
        }
    }
    
    getPriorityLevel(prioridad) {
        const mapping = {
            'critica': 'critical',
            'alta': 'high',
            'media': 'normal',
            'baja': 'low'
        };
        return mapping[prioridad] || 'normal';
    }
    
    flashNotificationIcon() {
        const icon = document.querySelector('#notificationsDropdown i');
        if (icon) {
            icon.classList.add('text-danger');
            icon.style.animation = 'pulse 1s infinite';
            
            setTimeout(() => {
                icon.classList.remove('text-danger');
                icon.style.animation = '';
            }, 10000);
        }
    }
    
    updateBadge(count) {
        const badge = document.getElementById('notificationBadge');
        if (badge) {
            if (count > 0) {
                badge.textContent = count > 99 ? '99+' : count;
                badge.style.display = 'block';
            } else {
                badge.style.display = 'none';
            }
        }
    }
    
    updateMenu(notifications, data = {}) {
        const menu = document.getElementById('notificationsMenu');
        if (!menu) return;
        
        if (notifications.length === 0) {
            menu.innerHTML = `
                <li><h6 class="dropdown-header">📢 Notificaciones</h6></li>
                <li><div class="dropdown-item-text text-center text-muted py-3">
                    <i class="bi bi-check-circle me-2"></i>
                    No hay notificaciones nuevas
                </div></li>
                ${this.getSettingsMenuItem()}
            `;
            return;
        }
        
        let menuHTML = '<li><h6 class="dropdown-header">📢 Notificaciones Recientes</h6></li>';
        
        notifications.forEach(notif => {
            const priorityClass = this.getPriorityClass(notif.prioridad);
            const icon = this.getPriorityIcon(notif.prioridad, notif.tipo);
            
            menuHTML += `
                <li>
                    <a class="dropdown-item notification-item" href="${notif.url}">
                        <div class="d-flex align-items-start">
                            <div class="notification-icon me-2">
                                ${icon}
                            </div>
                            <div class="flex-grow-1">
                                <h6 class="mb-1 ${priorityClass}">${notif.titulo}</h6>
                                <p class="mb-0 small text-muted">${notif.mensaje}</p>
                            </div>
                            <small class="text-muted ms-2">${notif.tiempo}</small>
                        </div>
                    </a>
                </li>
            `;
        });
        
        // Agregar resumen
        if (data.mis_pendientes !== undefined) {
            menuHTML += `
                <li><hr class="dropdown-divider"></li>
                <li>
                    <div class="dropdown-item-text small">
                        <div class="row text-center">
                            <div class="col-4">
                                <strong class="text-primary">${data.mis_pendientes}</strong><br>
                                <small>Mis tickets</small>
                            </div>
                            <div class="col-4">
                                <strong class="text-info">${notifications.length}</strong><br>
                                <small>Nuevos</small>
                            </div>
                            <div class="col-4">
                                <strong class="text-danger">${data.total_criticos || 0}</strong><br>
                                <small>Críticos</small>
                            </div>
                        </div>
                    </div>
                </li>
            `;
        }
        
        menuHTML += this.getSettingsMenuItem();
        menu.innerHTML = menuHTML;
    }
    
    getPriorityClass(prioridad) {
        const classes = {
            'critica': 'text-danger fw-bold',
            'alta': 'text-warning fw-semibold',
            'media': 'text-primary',
            'baja': 'text-muted'
        };
        return classes[prioridad] || 'text-primary';
    }
    
    getPriorityIcon(prioridad, tipo) {
        if (prioridad === 'critica') return '🚨';
        if (tipo === 'nuevo_ticket') return '🎫';
        return '🔔';
    }
    
    getSettingsMenuItem() {
        return `
            <li><hr class="dropdown-divider"></li>
            <li>
                <a class="dropdown-item" href="#" onclick="notificationManager.showSettings(); return false;">
                    <i class="bi bi-gear me-2"></i>Configurar notificaciones
                </a>
            </li>
        `;
    }
    
    showSettings() {
        // Crear modal de configuración
        const modalHTML = `
            <div class="modal fade" id="notificationSettingsModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">⚙️ Configuración de Notificaciones</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="mb-3">
                                <div class="form-check form-switch">
                                    <input class="form-check-input" type="checkbox" id="soundEnabled" ${this.settings.soundEnabled ? 'checked' : ''}>
                                    <label class="form-check-label" for="soundEnabled">
                                        🔊 Reproducir sonidos
                                    </label>
                                </div>
                            </div>
                            <div class="mb-3">
                                <div class="form-check form-switch">
                                    <input class="form-check-input" type="checkbox" id="pushEnabled" ${this.settings.pushEnabled ? 'checked' : ''}>
                                    <label class="form-check-label" for="pushEnabled">
                                        📱 Notificaciones del navegador
                                    </label>
                                </div>
                            </div>
                            <div class="mb-3">
                                <div class="form-check form-switch">
                                    <input class="form-check-input" type="checkbox" id="criticalOnly" ${this.settings.criticalOnly ? 'checked' : ''}>
                                    <label class="form-check-label" for="criticalOnly">
                                        🚨 Solo tickets críticos
                                    </label>
                                </div>
                            </div>
                            <div class="mb-3">
                                <label for="soundVolume" class="form-label">🔊 Volumen del sonido</label>
                                <input type="range" class="form-range" id="soundVolume" min="0" max="1" step="0.1" value="${this.settings.soundVolume}">
                            </div>
                            <div class="mb-3">
                                <label for="refreshInterval" class="form-label">🔄 Intervalo de actualización (segundos)</label>
                                <select class="form-select" id="refreshInterval">
                                    <option value="15000" ${this.settings.autoRefreshInterval === 15000 ? 'selected' : ''}>15 segundos</option>
                                    <option value="30000" ${this.settings.autoRefreshInterval === 30000 ? 'selected' : ''}>30 segundos</option>
                                    <option value="60000" ${this.settings.autoRefreshInterval === 60000 ? 'selected' : ''}>1 minuto</option>
                                    <option value="300000" ${this.settings.autoRefreshInterval === 300000 ? 'selected' : ''}>5 minutos</option>
                                </select>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                            <button type="button" class="btn btn-primary" onclick="notificationManager.saveSettingsFromModal()">Guardar</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Remover modal existente si existe
        const existingModal = document.getElementById('notificationSettingsModal');
        if (existingModal) existingModal.remove();
        
        // Agregar nuevo modal
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        
        // Mostrar modal
        const modal = new bootstrap.Modal(document.getElementById('notificationSettingsModal'));
        modal.show();
    }
    
    saveSettingsFromModal() {
        this.settings.soundEnabled = document.getElementById('soundEnabled').checked;
        this.settings.pushEnabled = document.getElementById('pushEnabled').checked;
        this.settings.criticalOnly = document.getElementById('criticalOnly').checked;
        this.settings.soundVolume = parseFloat(document.getElementById('soundVolume').value);
        this.settings.autoRefreshInterval = parseInt(document.getElementById('refreshInterval').value);
        
        this.saveSettings();
        this.applySettings();
        
        // Cerrar modal
        bootstrap.Modal.getInstance(document.getElementById('notificationSettingsModal')).hide();
        
        this.showToast('✅ Configuración guardada', 'success');
    }
}

// Inicializar el gestor de notificaciones
const notificationManager = new NotificationManager();

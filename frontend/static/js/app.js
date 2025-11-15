// FocusIT JavaScript Application

// Global Configuration
const FocusIT = {
    config: {
        searchDelay: 500,
        autoRefreshInterval: 30000,
        animationDuration: 300
    },
    
    // Initialize application
    init() {
        this.setupEventListeners();
        this.initializeComponents();
        this.setupAutoRefresh();
    },
    
    // Setup global event listeners
    setupEventListeners() {
        // Global search functionality
        document.addEventListener('DOMContentLoaded', () => {
            this.initSearch();
            this.initTooltips();
            this.initModals();
            this.initForms();
        });
        
        // Handle navigation
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-action]')) {
                this.handleAction(e.target.dataset.action, e.target);
            }
        });
        
        // Handle keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            this.handleKeyboardShortcuts(e);
        });
    },
    
    // Initialize search functionality
    initSearch() {
        const searchInputs = document.querySelectorAll('[data-search]');
        
        searchInputs.forEach(input => {
            let searchTimeout;
            
            input.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                const query = e.target.value.trim();
                const searchType = e.target.dataset.search;
                
                if (query.length >= 2) {
                    searchTimeout = setTimeout(() => {
                        this.performSearch(query, searchType, e.target);
                    }, this.config.searchDelay);
                } else {
                    this.clearSearchResults(e.target);
                }
            });
        });
    },
    
    // Perform search based on type
    performSearch(query, type, inputElement) {
        const resultsContainer = this.getSearchResultsContainer(inputElement);
        
        if (!resultsContainer) return;
        
        // Show loading state
        this.showSearchLoading(resultsContainer);
        
        let searchUrl;
        switch (type) {
            case 'knowledge':
                searchUrl = '/knowledge/buscar_sugerencias';
                break;
            case 'tickets':
                searchUrl = '/tickets/buscar_articulos';
                break;
            case 'dashboard':
                searchUrl = '/dashboard/buscar_ayuda';
                break;
            default:
                return;
        }
        
        fetch(`${searchUrl}?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                this.displaySearchResults(data, resultsContainer, type);
            })
            .catch(error => {
                console.error('Search error:', error);
                this.showSearchError(resultsContainer);
            });
    },
    
    // Display search results
    displaySearchResults(results, container, type) {
        if (results.length === 0) {
            container.innerHTML = `
                <div class="alert alert-info">
                    <i class="bi bi-info-circle me-2"></i>
                    No se encontraron resultados
                </div>
            `;
            return;
        }
        
        let html = '<div class="list-group">';
        
        results.forEach(item => {
            switch (type) {
                case 'knowledge':
                    html += this.renderKnowledgeResult(item);
                    break;
                case 'tickets':
                    html += this.renderTicketResult(item);
                    break;
                case 'dashboard':
                    html += this.renderDashboardResult(item);
                    break;
            }
        });
        
        html += '</div>';
        container.innerHTML = html;
    },
    
    // Render knowledge base result
    renderKnowledgeResult(item) {
        return `
            <a href="/knowledge/articulo/${item.id}" class="list-group-item list-group-item-action">
                <div class="d-flex w-100 justify-content-between">
                    <h6 class="mb-1">${item.titulo}</h6>
                    <small class="text-muted">${item.categoria}</small>
                </div>
            </a>
        `;
    },
    
    // Render ticket result
    renderTicketResult(item) {
        return `
            <a href="${item.url}" target="_blank" class="list-group-item list-group-item-action">
                <div class="d-flex w-100 justify-content-between">
                    <h6 class="mb-1">${item.titulo}</h6>
                    <small class="text-muted">Artículo</small>
                </div>
                <p class="mb-1 text-muted small">${item.contenido_preview}</p>
            </a>
        `;
    },
    
    // Render dashboard result
    renderDashboardResult(item) {
        return `
            <a href="/knowledge/articulo/${item.id}" class="list-group-item list-group-item-action">
                <div class="d-flex w-100 justify-content-between">
                    <h6 class="mb-1">${item.titulo}</h6>
                    <small class="text-muted"><i class="bi bi-eye me-1"></i>${item.vistas}</small>
                </div>
                <p class="mb-1 text-muted small">${item.contenido}</p>
            </a>
        `;
    },
    
    // Get search results container
    getSearchResultsContainer(inputElement) {
        const containerId = inputElement.dataset.resultsContainer;
        return containerId ? document.getElementById(containerId) : 
               inputElement.parentElement.querySelector('.search-results');
    },
    
    // Show search loading state
    showSearchLoading(container) {
        container.innerHTML = `
            <div class="text-center p-3">
                <div class="spinner-border spinner-border-sm text-primary" role="status">
                    <span class="visually-hidden">Buscando...</span>
                </div>
                <div class="mt-2 text-muted small">Buscando...</div>
            </div>
        `;
    },
    
    // Show search error
    showSearchError(container) {
        container.innerHTML = `
            <div class="alert alert-danger">
                <i class="bi bi-exclamation-triangle me-2"></i>
                Error al realizar la búsqueda. Intenta nuevamente.
            </div>
        `;
    },
    
    // Clear search results
    clearSearchResults(inputElement) {
        const container = this.getSearchResultsContainer(inputElement);
        if (container) {
            container.innerHTML = '';
        }
    },
    
    // Initialize tooltips
    initTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    },
    
    // Initialize modals
    initModals() {
        // Auto-focus first input in modals
        document.addEventListener('shown.bs.modal', function (e) {
            const firstInput = e.target.querySelector('input, textarea, select');
            if (firstInput) {
                firstInput.focus();
            }
        });
    },
    
    // Initialize forms
    initForms() {
        // Form validation
        const forms = document.querySelectorAll('.needs-validation');
        
        Array.from(forms).forEach(form => {
            form.addEventListener('submit', (event) => {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            });
        });
        
        // Auto-save drafts
        this.initAutoSave();
    },
    
    // Initialize auto-save functionality
    initAutoSave() {
        const autoSaveForms = document.querySelectorAll('[data-auto-save]');
        
        autoSaveForms.forEach(form => {
            const formId = form.dataset.autoSave;
            
            // Load saved data
            this.loadFormData(form, formId);
            
            // Save on input
            form.addEventListener('input', () => {
                this.saveFormData(form, formId);
            });
        });
    },
    
    // Save form data to localStorage
    saveFormData(form, formId) {
        const formData = new FormData(form);
        const data = {};
        
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }
        
        localStorage.setItem(`focusit_draft_${formId}`, JSON.stringify(data));
    },
    
    // Load form data from localStorage
    loadFormData(form, formId) {
        const savedData = localStorage.getItem(`focusit_draft_${formId}`);
        
        if (savedData) {
            try {
                const data = JSON.parse(savedData);
                
                Object.keys(data).forEach(key => {
                    const input = form.querySelector(`[name="${key}"]`);
                    if (input && input.type !== 'file') {
                        input.value = data[key];
                    }
                });
            } catch (error) {
                console.error('Error loading form data:', error);
            }
        }
    },
    
    // Clear saved form data
    clearFormData(formId) {
        localStorage.removeItem(`focusit_draft_${formId}`);
    },
    
    // Handle custom actions
    handleAction(action, element) {
        switch (action) {
            case 'copy-link':
                this.copyToClipboard(window.location.href, element);
                break;
            case 'share-whatsapp':
                this.shareWhatsApp(element.dataset.text || document.title);
                break;
            case 'print':
                window.print();
                break;
            case 'refresh':
                location.reload();
                break;
            default:
                console.warn('Unknown action:', action);
        }
    },
    
    // Copy text to clipboard
    copyToClipboard(text, element) {
        navigator.clipboard.writeText(text).then(() => {
            this.showToast('Enlace copiado al portapapeles', 'success');
            
            // Visual feedback
            if (element) {
                const originalText = element.innerHTML;
                element.innerHTML = '<i class="bi bi-check me-2"></i>¡Copiado!';
                element.classList.add('btn-success');
                
                setTimeout(() => {
                    element.innerHTML = originalText;
                    element.classList.remove('btn-success');
                }, 2000);
            }
        }).catch(err => {
            console.error('Error copying to clipboard:', err);
            this.showToast('Error al copiar enlace', 'error');
        });
    },
    
    // Share via WhatsApp
    shareWhatsApp(text) {
        const url = `https://wa.me/?text=${encodeURIComponent(text + '\n' + window.location.href)}`;
        window.open(url, '_blank');
    },
    
    // Show toast notification
    showToast(message, type = 'info') {
        const toastContainer = this.getOrCreateToastContainer();
        const toastId = 'toast_' + Date.now();
        
        const toastHtml = `
            <div id="${toastId}" class="toast align-items-center text-white bg-${type === 'error' ? 'danger' : type}" role="alert">
                <div class="d-flex">
                    <div class="toast-body">
                        <i class="bi bi-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-triangle' : 'info-circle'} me-2"></i>
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;
        
        toastContainer.insertAdjacentHTML('beforeend', toastHtml);
        
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement);
        toast.show();
        
        // Remove from DOM after hiding
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    },
    
    // Get or create toast container
    getOrCreateToastContainer() {
        let container = document.getElementById('toast-container');
        
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            container.style.zIndex = '1055';
            document.body.appendChild(container);
        }
        
        return container;
    },
    
    // Handle keyboard shortcuts
    handleKeyboardShortcuts(e) {
        // Ctrl/Cmd + K for search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('input[type="search"], input[placeholder*="buscar" i]');
            if (searchInput) {
                searchInput.focus();
            }
        }
        
        // Escape to close modals/dropdowns
        if (e.key === 'Escape') {
            const openModal = document.querySelector('.modal.show');
            if (openModal) {
                bootstrap.Modal.getInstance(openModal).hide();
            }
        }
    },
    
    // Setup auto-refresh for certain pages
    setupAutoRefresh() {
        const autoRefreshElements = document.querySelectorAll('[data-auto-refresh]');
        
        autoRefreshElements.forEach(element => {
            const interval = parseInt(element.dataset.autoRefresh) || this.config.autoRefreshInterval;
            
            setInterval(() => {
                // Only refresh if user is not actively interacting
                if (!document.activeElement || 
                    (document.activeElement.tagName !== 'INPUT' && 
                     document.activeElement.tagName !== 'TEXTAREA')) {
                    this.refreshElement(element);
                }
            }, interval);
        });
    },
    
    // Refresh specific element content
    refreshElement(element) {
        const url = element.dataset.refreshUrl || window.location.href;
        
        fetch(url, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.text())
        .then(html => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const newElement = doc.querySelector(`[data-auto-refresh="${element.dataset.autoRefresh}"]`);
            
            if (newElement) {
                element.innerHTML = newElement.innerHTML;
                this.initializeComponents(); // Re-initialize components in refreshed content
            }
        })
        .catch(error => {
            console.error('Auto-refresh error:', error);
        });
    },
    
    // Initialize components after DOM changes
    initializeComponents() {
        this.initTooltips();
        // Re-initialize other components as needed
    },
    
    // Utility functions
    utils: {
        // Format date
        formatDate(date, format = 'dd/mm/yyyy') {
            const d = new Date(date);
            const day = String(d.getDate()).padStart(2, '0');
            const month = String(d.getMonth() + 1).padStart(2, '0');
            const year = d.getFullYear();
            
            return format
                .replace('dd', day)
                .replace('mm', month)
                .replace('yyyy', year);
        },
        
        // Format time
        formatTime(date) {
            return new Date(date).toLocaleTimeString('es-ES', {
                hour: '2-digit',
                minute: '2-digit'
            });
        },
        
        // Debounce function
        debounce(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        },
        
        // Throttle function
        throttle(func, limit) {
            let inThrottle;
            return function() {
                const args = arguments;
                const context = this;
                if (!inThrottle) {
                    func.apply(context, args);
                    inThrottle = true;
                    setTimeout(() => inThrottle = false, limit);
                }
            };
        }
    }
};

// Initialize application when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => FocusIT.init());
} else {
    FocusIT.init();
}

// Export for global access
window.FocusIT = FocusIT;

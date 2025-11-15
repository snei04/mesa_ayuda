from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import LoginManager, login_required, current_user
from config import Config
from models import db, Usuario, Ticket, ComentarioTicket, BaseConocimiento, SesionChatbot
import os

def create_app():
    # Configurar rutas para templates y static en la carpeta frontend
    frontend_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
    template_folder = os.path.join(frontend_folder, 'templates')
    static_folder = os.path.join(frontend_folder, 'static')
    
    app = Flask(__name__, 
                template_folder=template_folder,
                static_folder=static_folder)
    app.config.from_object(Config)
    
    # Inicializar extensiones
    db.init_app(app)
    
    # Configurar Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    
    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))
    
    # Registrar blueprints de rutas web (HTML)
    from routes.auth import auth_bp
    from routes.tickets import tickets_bp
    from routes.dashboard import dashboard_bp
    from routes.knowledge import knowledge_bp
    from routes.chatbot import chatbot_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(tickets_bp, url_prefix='/tickets')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(knowledge_bp, url_prefix='/knowledge')
    app.register_blueprint(chatbot_bp, url_prefix='/chatbot')
    
    # Registrar blueprints de API (JSON)
    from api import api_bp
    app.register_blueprint(api_bp)
    
    # Ruta principal
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.home'))
        return render_template('index.html')
    
    # Contexto global para templates
    @app.context_processor
    def inject_config():
        return {
            'MAIN_CATEGORIES': Config.MAIN_CATEGORIES,
            'TICKET_STATES': Config.TICKET_STATES,
            'TICKET_PRIORITIES': Config.TICKET_PRIORITIES
        }
    
    # Manejo de errores centralizado para API
    from utils.api_response import APIResponse, APIError
    
    @app.errorhandler(404)
    def not_found(error):
        # Si es una petición a la API, devolver JSON
        if request.path.startswith('/api/'):
            return APIResponse.error(
                APIError.NOT_FOUND,
                'Recurso no encontrado',
                404
            )
        # Si no, renderizar página HTML
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        # Si es una petición a la API, devolver JSON
        if request.path.startswith('/api/'):
            return APIResponse.error(
                APIError.INTERNAL_ERROR,
                'Error interno del servidor',
                500
            )
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden(error):
        if request.path.startswith('/api/'):
            return APIResponse.error(
                APIError.FORBIDDEN,
                'No tienes permisos para acceder a este recurso',
                403
            )
        return render_template('errors/403.html'), 403
    
    # Manejo de errores de validación de Flask
    @app.errorhandler(400)
    def bad_request(error):
        if request.path.startswith('/api/'):
            return APIResponse.error(
                APIError.VALIDATION_ERROR,
                'Solicitud inválida',
                400
            )
        return render_template('errors/400.html'), 400
    
    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)

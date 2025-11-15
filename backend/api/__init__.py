"""
API REST para FocusIT
Todas las rutas devuelven JSON consistente
"""
from flask import Blueprint

# Blueprint principal de la API
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Importar sub-blueprints
from api.auth import auth_api_bp
from api.tickets import tickets_api_bp
from api.knowledge import knowledge_api_bp
from api.dashboard import dashboard_api_bp
from api.chatbot import chatbot_api_bp

# Registrar sub-blueprints
api_bp.register_blueprint(auth_api_bp, url_prefix='/auth')
api_bp.register_blueprint(tickets_api_bp, url_prefix='/tickets')
api_bp.register_blueprint(knowledge_api_bp, url_prefix='/knowledge')
api_bp.register_blueprint(dashboard_api_bp, url_prefix='/dashboard')
api_bp.register_blueprint(chatbot_api_bp, url_prefix='/chatbot')

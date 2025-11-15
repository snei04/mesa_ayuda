import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///focusit.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # WhatsApp Business API Configuration
    WHATSAPP_TOKEN = os.environ.get('WHATSAPP_TOKEN')
    WHATSAPP_VERIFY_TOKEN = os.environ.get('WHATSAPP_VERIFY_TOKEN')
    
    # Estados de tickets definidos
    TICKET_STATES = [
        'nuevo',
        'asignado_a_tecnico', 
        'en_proceso',
        'esperando_aprobacion',
        'esperando_respuesta_usuario',
        'resuelto',
        'cerrado'
    ]
    
    # Prioridades de tickets
    TICKET_PRIORITIES = [
        'baja',
        'media', 
        'alta',
        'critica'
    ]
    
    # Categorías principales del sistema
    MAIN_CATEGORIES = {
        'problemas_tecnicos': {
            'name': 'Problemas Técnicos',
            'subcategories': {
                'computador_celular': 'Computador o Celular',
                'impresoras': 'Impresoras',
                'software_optica': 'Aplicativo o Software AgilMed'
            }
        },
        'solicitudes_software': {
            'name': 'Solicitudes de Software',
            'subcategories': {
                'actualizaciones': 'Actualizaciones',
                'instalaciones': 'Instalaciones'
            }
        },
        'permisos_accesos': {
            'name': 'Permisos y Accesos',
            'subcategories': {
                'carpetas_compartidas': 'Carpetas Compartidas',
                'sistemas_internos': 'Sistemas Internos',
                'reset_password': 'Restablecer Contraseña'
            }
        },
        'consultas_generales': {
            'name': 'Consultas Generales',
            'subcategories': {
                'capacitacion': 'Capacitación',
                'procedimientos': 'Procedimientos',
                'soporte_general': 'Soporte General'
            }
        }
    }

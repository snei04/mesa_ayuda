from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=True) # Nuevo campo contraseña
    telefono = db.Column(db.String(20), nullable=True)
    departamento = db.Column(db.String(50), nullable=True)
    cargo = db.Column(db.String(50), nullable=True)
    es_tecnico = db.Column(db.Boolean, default=False)
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    tickets_creados = db.relationship('Ticket', foreign_keys='Ticket.usuario_id', backref='usuario', lazy='dynamic')
    tickets_asignados = db.relationship('Ticket', foreign_keys='Ticket.tecnico_id', backref='tecnico', lazy='dynamic')
    comentarios = db.relationship('ComentarioTicket', backref='autor', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<Usuario {self.nombre}>'

class Ticket(db.Model):
    __tablename__ = 'tickets'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    tecnico_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    categoria = db.Column(db.String(50), nullable=False)
    subcategoria = db.Column(db.String(50), nullable=True)
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    estado = db.Column(db.String(30), default='nuevo')
    prioridad = db.Column(db.String(20), default='media')
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    fecha_cierre = db.Column(db.DateTime, nullable=True)
    
    # Campos adicionales para el flujo guiado
    origen = db.Column(db.String(20), default='portal')  # portal, whatsapp, email
    datos_adicionales = db.Column(db.JSON, nullable=True)  # Para almacenar respuestas del flujo guiado
    
    # Relaciones
    comentarios = db.relationship('ComentarioTicket', backref='ticket', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Ticket {self.id}: {self.titulo}>'
    
    def get_estado_display(self):
        estados_display = {
            'nuevo': 'Nuevo',
            'asignado_a_tecnico': 'Asignado a Técnico',
            'en_proceso': 'En Proceso',
            'esperando_aprobacion': 'Esperando Aprobación',
            'esperando_respuesta_usuario': 'Esperando Respuesta del Usuario',
            'resuelto': 'Resuelto',
            'cerrado': 'Cerrado'
        }
        return estados_display.get(self.estado, self.estado)
    
    def get_prioridad_display(self):
        prioridades_display = {
            'baja': 'Baja',
            'media': 'Media',
            'alta': 'Alta',
            'critica': 'Crítica'
        }
        return prioridades_display.get(self.prioridad, self.prioridad)

class ComentarioTicket(db.Model):
    __tablename__ = 'comentarios_tickets'
    
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False)
    autor_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    es_interno = db.Column(db.Boolean, default=False)  # Para comentarios solo visibles por técnicos
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Comentario {self.id} del Ticket {self.ticket_id}>'

class BaseConocimiento(db.Model):
    __tablename__ = 'base_conocimiento'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    palabras_clave = db.Column(db.String(500), nullable=True)
    categoria = db.Column(db.String(50), nullable=True)
    subcategoria = db.Column(db.String(50), nullable=True)
    activo = db.Column(db.Boolean, default=True)
    vistas = db.Column(db.Integer, default=0)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    autor_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    # Relaciones
    autor = db.relationship('Usuario', backref='articulos_conocimiento')
    pasos = db.relationship('PasoGuia', backref='articulo', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Artículo {self.titulo}>'
    
    def incrementar_vistas(self):
        self.vistas += 1
        db.session.commit()

class PasoGuia(db.Model):
    __tablename__ = 'pasos_guia'
    
    id = db.Column(db.Integer, primary_key=True)
    articulo_id = db.Column(db.Integer, db.ForeignKey('base_conocimiento.id'), nullable=False)
    orden = db.Column(db.Integer, nullable=False)
    titulo = db.Column(db.String(200), nullable=True)
    contenido = db.Column(db.Text, nullable=True)
    imagen_url = db.Column(db.String(500), nullable=True)
    
    def __repr__(self):
        return f'<Paso {self.orden} del Artículo {self.articulo_id}>'



class HistorialChat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sesion_id = db.Column(db.Integer, db.ForeignKey('sesiones_chatbot.id'))
    emisor = db.Column(db.String(10)) # 'usuario' o 'bot'
    mensaje = db.Column(db.Text)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

class SesionChatbot(db.Model):
    __tablename__ = 'sesiones_chatbot'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_telefono = db.Column(db.String(20), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    estado_conversacion = db.Column(db.String(50), default='inicio')
    datos_temporales = db.Column(db.JSON, nullable=True)  # Para almacenar datos durante el flujo
    fecha_inicio = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_ultima_actividad = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    activa = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Sesión Chatbot {self.usuario_telefono}>'


        

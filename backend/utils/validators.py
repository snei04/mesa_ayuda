"""
Validadores para las tres capas de seguridad
Siguiendo las reglas globales: Frontend, Backend, Base de Datos
"""
import re
from typing import Tuple, Optional


class Validator:
    """Validadores reutilizables para backend"""
    
    @staticmethod
    def email(email: str) -> Tuple[bool, Optional[str]]:
        """
        Valida formato de email
        
        Returns:
            (is_valid, error_message)
        """
        if not email:
            return False, 'El email es requerido'
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, 'Formato de email inválido'
        
        if len(email) > 255:
            return False, 'El email es demasiado largo'
            
        return True, None
    
    @staticmethod
    def telefono(telefono: str) -> Tuple[bool, Optional[str]]:
        """
        Valida formato de teléfono (formato colombiano)
        
        Returns:
            (is_valid, error_message)
        """
        if not telefono:
            return True, None  # Teléfono es opcional
        
        # Remover espacios y caracteres especiales
        telefono_limpio = re.sub(r'[^\d+]', '', telefono)
        
        # Validar formato: +57XXXXXXXXXX o XXXXXXXXXX
        if not re.match(r'^(\+57)?[0-9]{10}$', telefono_limpio):
            return False, 'Formato de teléfono inválido (debe ser 10 dígitos)'
            
        return True, None
    
    @staticmethod
    def texto_requerido(texto: str, nombre_campo: str, min_length: int = 1, max_length: int = 500) -> Tuple[bool, Optional[str]]:
        """
        Valida campo de texto requerido
        
        Args:
            texto: Texto a validar
            nombre_campo: Nombre del campo para mensajes de error
            min_length: Longitud mínima
            max_length: Longitud máxima
            
        Returns:
            (is_valid, error_message)
        """
        if not texto or not texto.strip():
            return False, f'{nombre_campo} es requerido'
        
        texto = texto.strip()
        
        if len(texto) < min_length:
            return False, f'{nombre_campo} debe tener al menos {min_length} caracteres'
        
        if len(texto) > max_length:
            return False, f'{nombre_campo} no puede exceder {max_length} caracteres'
            
        return True, None
    
    @staticmethod
    def numero_positivo(valor: any, nombre_campo: str) -> Tuple[bool, Optional[str]]:
        """
        Valida que un valor sea un número positivo
        
        Returns:
            (is_valid, error_message)
        """
        try:
            numero = float(valor)
            if numero < 0:
                return False, f'{nombre_campo} debe ser un número positivo'
            return True, None
        except (ValueError, TypeError):
            return False, f'{nombre_campo} debe ser un número válido'
    
    @staticmethod
    def opcion_valida(valor: str, opciones: list, nombre_campo: str) -> Tuple[bool, Optional[str]]:
        """
        Valida que un valor esté dentro de opciones permitidas
        
        Returns:
            (is_valid, error_message)
        """
        if valor not in opciones:
            return False, f'{nombre_campo} debe ser una de las siguientes opciones: {", ".join(opciones)}'
        return True, None
    
    @staticmethod
    def sanitize_html(texto: str) -> str:
        """
        Sanitiza texto removiendo HTML peligroso
        Básico - para producción usar bleach o similar
        """
        if not texto:
            return texto
        
        # Remover tags HTML básicos
        texto = re.sub(r'<script[^>]*>.*?</script>', '', texto, flags=re.DOTALL | re.IGNORECASE)
        texto = re.sub(r'<iframe[^>]*>.*?</iframe>', '', texto, flags=re.DOTALL | re.IGNORECASE)
        texto = re.sub(r'on\w+="[^"]*"', '', texto, flags=re.IGNORECASE)
        
        return texto
    
    @staticmethod
    def sanitize_sql(texto: str) -> str:
        """
        Sanitiza texto para prevenir SQL injection básico
        NOTA: Usar siempre parameterized queries como primera línea de defensa
        """
        if not texto:
            return texto
        
        # Remover caracteres peligrosos comunes en SQL injection
        peligrosos = ["'", '"', ';', '--', '/*', '*/', 'xp_', 'sp_', 'DROP', 'DELETE', 'INSERT', 'UPDATE']
        
        for peligroso in peligrosos:
            texto = texto.replace(peligroso, '')
        
        return texto


class TicketValidator:
    """Validadores específicos para tickets"""
    
    @staticmethod
    def validar_creacion(data: dict) -> Tuple[bool, dict]:
        """
        Valida datos para crear un ticket
        
        Returns:
            (is_valid, errors_dict)
        """
        errors = {}
        
        # Validar título
        is_valid, error = Validator.texto_requerido(
            data.get('titulo', ''), 
            'Título', 
            min_length=5, 
            max_length=200
        )
        if not is_valid:
            errors['titulo'] = error
        
        # Validar descripción
        is_valid, error = Validator.texto_requerido(
            data.get('descripcion', ''), 
            'Descripción', 
            min_length=10, 
            max_length=2000
        )
        if not is_valid:
            errors['descripcion'] = error
        
        # Validar categoría
        if not data.get('categoria'):
            errors['categoria'] = 'Categoría es requerida'
        
        # Validar prioridad
        prioridades_validas = ['baja', 'media', 'alta', 'critica']
        prioridad = data.get('prioridad', 'media')
        is_valid, error = Validator.opcion_valida(
            prioridad, 
            prioridades_validas, 
            'Prioridad'
        )
        if not is_valid:
            errors['prioridad'] = error
        
        return len(errors) == 0, errors


class UsuarioValidator:
    """Validadores específicos para usuarios"""
    
    @staticmethod
    def validar_registro(data: dict) -> Tuple[bool, dict]:
        """
        Valida datos para registrar un usuario
        
        Returns:
            (is_valid, errors_dict)
        """
        errors = {}
        
        # Validar nombre
        is_valid, error = Validator.texto_requerido(
            data.get('nombre', ''), 
            'Nombre', 
            min_length=2, 
            max_length=100
        )
        if not is_valid:
            errors['nombre'] = error
        
        # Validar email
        is_valid, error = Validator.email(data.get('email', ''))
        if not is_valid:
            errors['email'] = error
        
        # Validar teléfono
        is_valid, error = Validator.telefono(data.get('telefono', ''))
        if not is_valid:
            errors['telefono'] = error
        
        # Validar departamento
        is_valid, error = Validator.texto_requerido(
            data.get('departamento', ''), 
            'Departamento', 
            min_length=2, 
            max_length=100
        )
        if not is_valid:
            errors['departamento'] = error
        
        # Validar cargo
        is_valid, error = Validator.texto_requerido(
            data.get('cargo', ''), 
            'Cargo', 
            min_length=2, 
            max_length=100
        )
        if not is_valid:
            errors['cargo'] = error
        
        return len(errors) == 0, errors


class ConocimientoValidator:
    """Validadores específicos para base de conocimiento"""
    
    @staticmethod
    def validar_articulo(data: dict) -> Tuple[bool, dict]:
        """
        Valida datos para crear/editar un artículo
        
        Returns:
            (is_valid, errors_dict)
        """
        errors = {}
        
        # Validar título
        is_valid, error = Validator.texto_requerido(
            data.get('titulo', ''), 
            'Título', 
            min_length=5, 
            max_length=200
        )
        if not is_valid:
            errors['titulo'] = error
        
        # Validar contenido
        is_valid, error = Validator.texto_requerido(
            data.get('contenido', ''), 
            'Contenido', 
            min_length=20, 
            max_length=10000
        )
        if not is_valid:
            errors['contenido'] = error
        
        # Validar categoría
        if not data.get('categoria'):
            errors['categoria'] = 'Categoría es requerida'
        
        return len(errors) == 0, errors

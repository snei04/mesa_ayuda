from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import db, Usuario
from utils.security import generate_magic_token, verify_magic_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.home'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email:
            flash('Por favor ingresa tu correo electrónico', 'error')
            return render_template('auth/login.html')
        
        usuario = Usuario.query.filter_by(email=email, activo=True).first()
        
        # Lógica Login Normal (Email + Password)
        if password:
            if usuario and usuario.check_password(password):
                login_user(usuario, remember=True)
                next_page = request.args.get('next')
                flash(f'¡Bienvenido/a de nuevo {usuario.nombre}!', 'success')
                return redirect(next_page) if next_page else redirect(url_for('dashboard.home'))
            else:
                flash('Correo o contraseña incorrectos', 'error')
                return render_template('auth/login.html')
        
        # Si no mandó contraseña, tal vez quería Magic Link (pero eso va por otra ruta, aquí error)
        flash('Por favor ingresa tu contraseña', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/magic-link', methods=['POST'])
def request_magic_link():
    """Genera y envía un enlace de acceso mágico"""
    email = request.form.get('email')
    if not email:
        flash('Por favor ingresa tu correo', 'error')
        return redirect(url_for('auth.login'))
    
    usuario = Usuario.query.filter_by(email=email, activo=True).first()
    
    if usuario:
        token = generate_magic_token(usuario.id)
        link = url_for('auth.magic_login', token=token, _external=True)
        
        # TODO: En producción, enviar esto por email real
        print("="*50)
        print(f"📧 MAGIC LINK PARA {email}:")
        print(f"{link}")
        print("="*50)
        
        flash(f'¡Enlace enviado! Revisa tu correo {email} (o la consola del servidor).', 'info')
    else:
        # Por seguridad, no decimos si el usuario existe o no, pero aquí para UX lo dejamos vago
        flash('Si tu cuenta existe, recibirás un enlace de acceso.', 'info')
        
    return redirect(url_for('auth.login'))

@auth_bp.route('/magic-login/<token>')
def magic_login(token):
    """Procesa el enlace mágico"""
    user_id = verify_magic_token(token)
    
    if not user_id:
        flash('El enlace de acceso es inválido o ha expirado.', 'error')
        return redirect(url_for('auth.login'))
        
    usuario = Usuario.query.get(user_id)
    if not usuario or not usuario.activo:
        flash('Usuario no válido.', 'error')
        return redirect(url_for('auth.login'))
        
    login_user(usuario, remember=True)
    flash(f'¡Hola {usuario.nombre}! Has ingresado vía enlace mágico ✨', 'success')
    return redirect(url_for('dashboard.home'))

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente', 'info')
    return redirect(url_for('index'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        password = request.form.get('password') # Nueva contraseña
        telefono = request.form.get('telefono')
        departamento = request.form.get('departamento')
        cargo = request.form.get('cargo')
        
        # Validaciones básicas
        if not all([nombre, email, password, departamento, cargo]):
            flash('Por favor completa todos los campos obligatorios', 'error')
            return render_template('auth/register.html')
        
        # Verificar si el email ya existe
        usuario_existente = Usuario.query.filter_by(email=email).first()
        if usuario_existente:
            flash('Ya existe un usuario con este correo electrónico', 'error')
            return render_template('auth/register.html')
        
        # Crear nuevo usuario
        nuevo_usuario = Usuario(
            nombre=nombre,
            email=email,
            telefono=telefono,
            departamento=departamento,
            cargo=cargo,
            es_tecnico=False,
            activo=True
        )
        nuevo_usuario.set_password(password) # Hashear contraseña
        
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        flash('Usuario registrado correctamente. Ya puedes iniciar sesión.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

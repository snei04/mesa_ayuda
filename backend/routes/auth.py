from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import db, Usuario

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.home'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        
        if not email:
            flash('Por favor ingresa tu correo electrónico', 'error')
            return render_template('auth/login.html')
        
        # Buscar usuario por email
        usuario = Usuario.query.filter_by(email=email, activo=True).first()
        
        if usuario:
            login_user(usuario, remember=True)
            next_page = request.args.get('next')
            flash(f'¡Bienvenido/a {usuario.nombre}!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('dashboard.home'))
        else:
            flash('Usuario no encontrado o inactivo', 'error')
    
    return render_template('auth/login.html')

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
        telefono = request.form.get('telefono')
        departamento = request.form.get('departamento')
        cargo = request.form.get('cargo')
        
        # Validaciones básicas
        if not all([nombre, email, departamento, cargo]):
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
        
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        flash('Usuario registrado correctamente. Ya puedes iniciar sesión.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

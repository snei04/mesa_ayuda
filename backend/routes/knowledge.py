from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from sqlalchemy import desc, or_
from models import db, BaseConocimiento, PasoGuia
from config import Config

knowledge_bp = Blueprint('knowledge', __name__)

# ... (código existente hasta la función crear)

@knowledge_bp.route('/')
@login_required
def index():
    # Parámetros de búsqueda y filtrado
    query = request.args.get('q', '').strip()
    categoria_filtro = request.args.get('categoria', '')
    page = request.args.get('page', 1, type=int)
    
    # Construir query base
    articulos_query = BaseConocimiento.query.filter_by(activo=True)
    
    # Aplicar filtros
    if query:
        articulos_query = articulos_query.filter(
            or_(
                BaseConocimiento.titulo.contains(query),
                BaseConocimiento.contenido.contains(query),
                BaseConocimiento.palabras_clave.contains(query)
            )
        )
    
    if categoria_filtro:
        articulos_query = articulos_query.filter_by(categoria=categoria_filtro)
    
    # Ordenar por relevancia (vistas) y fecha
    articulos = articulos_query.order_by(
        desc(BaseConocimiento.vistas),
        desc(BaseConocimiento.fecha_creacion)
    ).paginate(page=page, per_page=12, error_out=False)
    
    # Artículos más populares para la sidebar
    articulos_populares = BaseConocimiento.query.filter_by(
        activo=True
    ).order_by(desc(BaseConocimiento.vistas)).limit(5).all()
    
    return render_template('knowledge/index.html',
                         articulos=articulos,
                         articulos_populares=articulos_populares,
                         query=query,
                         categoria_filtro=categoria_filtro)

@knowledge_bp.route('/articulo/<int:id>')
@login_required
def articulo(id):
    articulo = BaseConocimiento.query.get_or_404(id)
    
    if not articulo.activo:
        flash('Este artículo no está disponible', 'error')
        return redirect(url_for('knowledge.index'))
    
    # Incrementar contador de vistas
    articulo.incrementar_vistas()
    
    # Artículos relacionados (misma categoría/subcategoría)
    articulos_relacionados = BaseConocimiento.query.filter(
        BaseConocimiento.id != id,
        BaseConocimiento.activo == True
    ).filter(
        or_(
            BaseConocimiento.categoria == articulo.categoria,
            BaseConocimiento.subcategoria == articulo.subcategoria
        )
    ).order_by(desc(BaseConocimiento.vistas)).limit(3).all()
    
    return render_template('knowledge/articulo.html',
                         articulo=articulo,
                         articulos_relacionados=articulos_relacionados)

@knowledge_bp.route('/crear', methods=['GET', 'POST'])

@login_required
def crear():
    if not current_user.es_tecnico:
        flash('Solo los técnicos pueden crear artículos de conocimiento', 'error')
        return redirect(url_for('knowledge.index'))
    
    categoria_preseleccionada = request.args.get('categoria', '')

    if request.method == 'POST':
        titulo = request.form.get('titulo')
        contenido = request.form.get('contenido')
        palabras_clave = request.form.get('palabras_clave')
        categoria = request.form.get('categoria')
        subcategoria = request.form.get('subcategoria')
        
        # Validaciones
        if not all([titulo, contenido, categoria]):
            flash('Por favor completa todos los campos obligatorios', 'error')
            return render_template('knowledge/crear.html', categoria_preseleccionada=categoria)
        
        # Crear artículo
        nuevo_articulo = BaseConocimiento(
            titulo=titulo,
            contenido=contenido,
            palabras_clave=palabras_clave,
            categoria=categoria,
            subcategoria=subcategoria,
            autor_id=current_user.id,
            activo=True
        )
        
        db.session.add(nuevo_articulo)
        db.session.flush() # Para obtener el ID del artículo

        # Procesar Pasos Guiados
        pasos_titulos = request.form.getlist('paso_titulo[]')
        pasos_contenidos = request.form.getlist('paso_contenido[]')
        pasos_imagenes = request.form.getlist('paso_imagen[]') # Por ahora URL, luego upload real

        for i in range(len(pasos_titulos)):
            if pasos_titulos[i].strip(): # Solo si tiene título
                nuevo_paso = PasoGuia(
                    articulo_id=nuevo_articulo.id,
                    orden=i + 1,
                    titulo=pasos_titulos[i],
                    contenido=pasos_contenidos[i] if i < len(pasos_contenidos) else "",
                    imagen_url=pasos_imagenes[i] if i < len(pasos_imagenes) else ""
                )
                db.session.add(nuevo_paso)
        
        db.session.commit()
        
        flash('Artículo creado exitosamente', 'success')
        return redirect(url_for('knowledge.articulo', id=nuevo_articulo.id))
    
    return render_template('knowledge/crear.html', categoria_preseleccionada=categoria_preseleccionada)

# ... (resto del código)

@knowledge_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    articulo = BaseConocimiento.query.get_or_404(id)
    
    # Solo el autor o administradores pueden editar
    if not current_user.es_tecnico or (articulo.autor_id != current_user.id):
        flash('No tienes permisos para editar este artículo', 'error')
        return redirect(url_for('knowledge.articulo', id=id))
    
    if request.method == 'POST':
        articulo.titulo = request.form.get('titulo')
        articulo.contenido = request.form.get('contenido')
        articulo.palabras_clave = request.form.get('palabras_clave')
        articulo.categoria = request.form.get('categoria')
        articulo.subcategoria = request.form.get('subcategoria')
        
        # Validaciones
        if not all([articulo.titulo, articulo.contenido, articulo.categoria]):
            flash('Por favor completa todos los campos obligatorios', 'error')
            return render_template('knowledge/editar.html', articulo=articulo)
        
        db.session.commit()
        flash('Artículo actualizado exitosamente', 'success')
        return redirect(url_for('knowledge.articulo', id=id))
    
    return render_template('knowledge/editar.html', articulo=articulo)

@knowledge_bp.route('/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar(id):
    articulo = BaseConocimiento.query.get_or_404(id)
    
    # Solo el autor o administradores pueden eliminar
    if not current_user.es_tecnico or (articulo.autor_id != current_user.id):
        flash('No tienes permisos para eliminar este artículo', 'error')
        return redirect(url_for('knowledge.articulo', id=id))
    
    # Marcar como inactivo en lugar de eliminar
    articulo.activo = False
    db.session.commit()
    
    flash('Artículo eliminado exitosamente', 'success')
    return redirect(url_for('knowledge.index'))

@knowledge_bp.route('/buscar_sugerencias')
@login_required
def buscar_sugerencias():
    """API endpoint para autocompletado de búsqueda"""
    query = request.args.get('q', '').strip()
    
    if len(query) < 2:
        return jsonify([])
    
    # Buscar títulos que coincidan
    sugerencias = BaseConocimiento.query.filter(
        BaseConocimiento.activo == True,
        BaseConocimiento.titulo.contains(query)
    ).order_by(desc(BaseConocimiento.vistas)).limit(5).all()
    
    return jsonify([{
        'titulo': art.titulo,
        'id': art.id,
        'categoria': art.categoria
    } for art in sugerencias])

@knowledge_bp.route('/por_categoria/<categoria>')
@login_required
def por_categoria(categoria):
    """Mostrar artículos de una categoría específica"""
    if categoria not in Config.MAIN_CATEGORIES:
        flash('Categoría no válida', 'error')
        return redirect(url_for('knowledge.index'))
    
    page = request.args.get('page', 1, type=int)
    subcategoria_filtro = request.args.get('subcategoria', '')
    
    # Construir query
    articulos_query = BaseConocimiento.query.filter_by(
        categoria=categoria,
        activo=True
    )
    
    if subcategoria_filtro:
        articulos_query = articulos_query.filter_by(subcategoria=subcategoria_filtro)
    
    articulos = articulos_query.order_by(
        desc(BaseConocimiento.vistas),
        desc(BaseConocimiento.fecha_creacion)
    ).paginate(page=page, per_page=12, error_out=False)
    
    categoria_info = Config.MAIN_CATEGORIES[categoria]
    
    return render_template('knowledge/categoria.html',
                         articulos=articulos,
                         categoria=categoria,
                         categoria_info=categoria_info,
                         subcategoria_filtro=subcategoria_filtro)

@knowledge_bp.route('/estadisticas')
@login_required
def estadisticas():
    """Estadísticas de la base de conocimiento (solo técnicos)"""
    if not current_user.es_tecnico:
        flash('No tienes permisos para ver las estadísticas', 'error')
        return redirect(url_for('knowledge.index'))
    
    # Artículos más vistos
    mas_vistos = BaseConocimiento.query.filter_by(
        activo=True
    ).order_by(desc(BaseConocimiento.vistas)).limit(10).all()
    
    # Artículos por categoría
    por_categoria = db.session.query(
        BaseConocimiento.categoria,
        db.func.count(BaseConocimiento.id).label('total'),
        db.func.sum(BaseConocimiento.vistas).label('vistas_totales')
    ).filter_by(activo=True).group_by(BaseConocimiento.categoria).all()
    
    # Autores más activos
    autores_activos = db.session.query(
        db.func.count(BaseConocimiento.id).label('articulos'),
        db.func.sum(BaseConocimiento.vistas).label('vistas_totales'),
        BaseConocimiento.autor_id
    ).filter_by(activo=True).group_by(BaseConocimiento.autor_id).all()
    
    return render_template('knowledge/estadisticas.html',
                         mas_vistos=mas_vistos,
                         por_categoria=por_categoria,
                         autores_activos=autores_activos)

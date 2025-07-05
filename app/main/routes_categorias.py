from flask import render_template, request, redirect, url_for, flash, jsonify
from . import main_bp
from app import db
from app.models import Categoria
from app.forms import CategoriaForm
from flask_login import login_required, current_user

@main_bp.route('/categorias')
@login_required
def listar_categorias():
    form = CategoriaForm()
    categorias = Categoria.query.filter_by(user_id=current_user.id).order_by(Categoria.nome).all()
    return render_template('main/categorias.html', categorias=categorias, form=form)

@main_bp.route('/categorias/adicionar', methods=['POST'])
@login_required
def adicionar_categoria():
    form = CategoriaForm()
    if form.validate_on_submit():
        existente = Categoria.query.filter_by(user_id=current_user.id, nome=form.nome.data).first()
        if existente:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest': return jsonify(success=False, errors={'nome': ['Uma categoria com este nome já existe.']}), 400
            flash('Uma categoria com este nome já existe.', 'danger')
        else: 
            nova_cat = Categoria(user_id=current_user.id, nome=form.nome.data, tipo=form.tipo.data)
            db.session.add(nova_cat); db.session.commit(); flash('Categoria adicionada!', 'success')
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest': return jsonify(success=True, redirect_url=url_for('main.listar_categorias'))
        return redirect(url_for('main.listar_categorias'))
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest': return jsonify(success=False, errors=form.errors), 400
    return redirect(url_for('main.listar_categorias'))

@main_bp.route('/categorias/editar/<int:id>', methods=['POST'])
@login_required
def editar_categoria(id):
    form = CategoriaForm()
    cat_a_editar = db.session.get(Categoria, id)
    if not cat_a_editar or cat_a_editar.user_id != current_user.id: return ('Acesso negado', 403)
    if form.validate_on_submit():
        existente = Categoria.query.filter_by(user_id=current_user.id, nome=form.nome.data).filter(Categoria.id != id).first()
        if existente:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest': return jsonify(success=False, errors={'nome': ['Uma outra categoria já possui este nome.']}), 400
            flash('Uma outra categoria já possui este nome.', 'danger')
        else: 
            cat_a_editar.nome = form.nome.data; cat_a_editar.tipo = form.tipo.data
            db.session.commit(); flash('Categoria atualizada!', 'success')
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest': return jsonify(success=True, redirect_url=url_for('main.listar_categorias'))
        return redirect(url_for('main.listar_categorias'))
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest': return jsonify(success=False, errors=form.errors), 400
    return redirect(url_for('main.listar_categorias'))

@main_bp.route('/categorias/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_categoria(id):
    categoria = db.session.get(Categoria, id)
    if not categoria or categoria.user_id != current_user.id: return ('Acesso negado', 403)
    if categoria.transacoes:
        flash('Não é possível excluir. Categoria está em uso.', 'danger')
    else: 
        db.session.delete(categoria); db.session.commit(); flash('Categoria excluída.', 'info')
    return redirect(url_for('main.listar_categorias'))

@main_bp.route('/categorias/adicionar/ajax', methods=['POST'])
@login_required
def adicionar_categoria_ajax():
    form = CategoriaForm(data=request.json)
    if form.validate():
        existente = Categoria.query.filter_by(user_id=current_user.id, nome=form.nome.data).first()
        if existente: return jsonify(success=False, errors={'nome': ['Uma categoria com este nome já existe.']})
        nova_cat = Categoria(user_id=current_user.id, nome=form.nome.data, tipo=form.tipo.data); db.session.add(nova_cat); db.session.commit()
        return jsonify(success=True, categoria={'id': nova_cat.id, 'nome': nova_cat.nome, 'tipo': nova_cat.tipo})
    return jsonify(success=False, errors=form.errors)
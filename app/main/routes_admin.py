from flask import render_template, request, redirect, url_for, flash, jsonify
from . import main_bp
from app import db
from app.models import Usuario
from app.forms import AdminUserCreateForm, AdminUserEditForm
from flask_login import login_required, current_user
from app.auth.routes import admin_required
from werkzeug.security import generate_password_hash

@main_bp.route('/admin/usuarios')
@login_required
@admin_required
def listar_usuarios():
    create_form = AdminUserCreateForm()
    edit_form = AdminUserEditForm()
    todos_usuarios = Usuario.query.filter(Usuario.id != current_user.id).order_by(Usuario.username).all()
    return render_template('main/admin_usuarios.html', usuarios=todos_usuarios, create_form=create_form, edit_form=edit_form)

@main_bp.route('/admin/usuarios/adicionar', methods=['POST'])
@login_required
@admin_required
def adicionar_usuario():
    form = AdminUserCreateForm()
    if form.validate_on_submit():
        username = form.username.data; email = form.email.data or None
        user_existente = Usuario.query.filter_by(username=username).first()
        email_existente = Usuario.query.filter_by(email=email).first() if email else None
        if user_existente: return jsonify(success=False, errors={'username': ['Este nome de usuário já está em uso.']}), 400
        if email_existente: return jsonify(success=False, errors={'email': ['Este e-mail já está em uso.']}), 400
        novo_usuario = Usuario(username=username, email=email, password=generate_password_hash(form.password.data), is_admin=form.is_admin.data)
        db.session.add(novo_usuario); db.session.commit(); flash(f"Usuário '{username}' criado com sucesso!", 'success')
        return jsonify(success=True, redirect_url=url_for('main.listar_usuarios'))
    return jsonify(success=False, errors=form.errors), 400

@main_bp.route('/admin/usuarios/editar/<int:id>', methods=['POST'])
@login_required
@admin_required
def editar_usuario(id):
    form = AdminUserEditForm()
    user_to_edit = db.session.get(Usuario, id)
    if not user_to_edit: return jsonify(success=False, errors={'geral': ['Usuário não encontrado.']}), 404
    if form.validate_on_submit():
        if form.email.data and form.email.data != user_to_edit.email:
            existente = Usuario.query.filter_by(email=form.email.data).first()
            if existente: return jsonify(success=False, errors={'email': ['Este e-mail já está em uso por outro usuário.']}), 400
        user_to_edit.email = form.email.data or None
        user_to_edit.is_admin = form.is_admin.data
        if form.password.data:
            user_to_edit.password = generate_password_hash(form.password.data)
        db.session.commit(); flash(f"Usuário '{user_to_edit.username}' atualizado com sucesso!", 'success')
        return jsonify(success=True, redirect_url=url_for('main.listar_usuarios'))
    return jsonify(success=False, errors=form.errors), 400

@main_bp.route('/admin/usuarios/excluir/<int:id>', methods=['POST'])
@login_required
@admin_required
def excluir_usuario(id):
    if id == current_user.id:
        flash('Você não pode excluir a si mesmo.', 'danger'); return redirect(url_for('main.listar_usuarios'))
    usuario_a_excluir = db.session.get(Usuario, id)
    if usuario_a_excluir:
        db.session.delete(usuario_a_excluir); db.session.commit()
        flash(f"Usuário '{usuario_a_excluir.username}' foi excluído com sucesso.", 'success')
    else:
        flash('Usuário não encontrado.', 'danger')
    return redirect(url_for('main.listar_usuarios'))
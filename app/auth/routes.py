from flask import render_template, request, redirect, url_for, flash, jsonify
from . import auth_bp
from app import db
from app.models import Usuario
from app.forms import LoginForm, PerfilForm
from flask_login import login_user, logout_user, login_required, current_user
import functools

def admin_required(view):
    """Decorador que restringe o acesso apenas a administradores."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not current_user.is_admin:
            flash('Você não tem permissão para acessar esta página.', 'danger')
            return redirect(url_for('main.index'))
        return view(**kwargs)
    return wrapped_view

@auth_bp.route('/login', methods=('GET', 'POST'))
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = Usuario.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Nome de usuário ou senha incorretos.', 'danger')
        else:
            # --- LÓGICA ATUALIZADA AQUI ---
            # O 'remember' agora depende do que o usuário marcou no formulário.
            login_user(user, remember=form.remember_me.data)
            
            # Redireciona para a próxima página ou para o index
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('main.index')
            return redirect(next_page)
            
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    user = db.session.get(Usuario, current_user.id)
    form = PerfilForm(obj=user)

    if form.validate_on_submit():
        if not user.check_password(form.senha_atual.data):
            flash('A senha atual está incorreta para salvar as alterações.', 'danger')
        else:
            user.email = form.email.data
            
            if form.nova_senha.data:
                user.set_password(form.nova_senha.data)
            
            db.session.commit()
            flash('Perfil atualizado com sucesso!', 'success')
            return redirect(url_for('auth.perfil'))
    
    return render_template('auth/perfil.html', form=form)

@auth_bp.route('/salvar-tema', methods=['POST'])
@login_required
def salvar_tema():
    novo_tema = request.json.get('theme')
    if novo_tema in ['light', 'dark', 'auto']:
        user = db.session.get(Usuario, current_user.id)
        user.theme = novo_tema
        db.session.commit()
        return jsonify(success=True)
    return jsonify(success=False), 400
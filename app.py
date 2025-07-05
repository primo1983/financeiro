import functools, json, locale, click, io, csv
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from flask import Flask, render_template, request, redirect, url_for, flash, session, g, jsonify, Response
import mysql.connector
from mysql.connector import errorcode
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, DateField, HiddenField, RadioField
from wtforms.validators import DataRequired, Email, EqualTo, Optional, Length, InputRequired
from werkzeug.security import generate_password_hash, check_password_hash
from decimal import Decimal

# --- CONFIGURAÇÃO INICIAL ---
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'uma-chave-secreta-muito-forte-e-diferente-para-producao'
csrf = CSRFProtect(app)

# --- CONFIGURAÇÃO DO MYSQL ---
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'financas'
app.config['MYSQL_PASSWORD'] = 'Mudar1234@'
app.config['MYSQL_DB'] = 'financas'

# --- CLASSES DE FORMULÁRIO (WTFORMS) ---
class LoginForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired("Este campo é obrigatório.")]); password = PasswordField('Senha', validators=[DataRequired("Este campo é obrigatório.")]); submit = SubmitField('Entrar')
class PerfilForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired("O e-mail é obrigatório."), Email("Por favor, insira um e-mail válido.")]); theme = RadioField('Tema', choices=[('auto', 'Sistema'), ('light', 'Claro'), ('dark', 'Escuro')], default='auto', validators=[DataRequired()]); senha_atual = PasswordField('Senha Atual', validators=[DataRequired(message="Sua senha atual é obrigatória.")]); nova_senha = PasswordField('Nova Senha', validators=[Optional(), Length(min=6, message="A nova senha deve ter pelo menos 6 caracteres.")]); confirmar_senha = PasswordField('Confirmar', validators=[EqualTo('nova_senha', message='As senhas não correspondem.')]); submit = SubmitField('Salvar Alterações')
class CategoriaForm(FlaskForm):
    id = HiddenField(); nome = StringField('Nome da Categoria', validators=[DataRequired()]); tipo = SelectField('Tipo', choices=[('Receita', 'Receita'), ('Despesa', 'Despesa'), ('Ambos', 'Ambos')], validators=[DataRequired()]); submit = SubmitField('Salvar')
class TransacaoForm(FlaskForm):
    id = HiddenField(); tipo = SelectField('Tipo', choices=[('Despesa', 'Despesa'), ('Receita', 'Receita')], validators=[DataRequired()]); categoria_id = SelectField('Categoria', coerce=int, validators=[InputRequired(message="Por favor, selecione uma categoria.")]); valor = StringField('Valor', validators=[DataRequired()]); data = DateField('Data', default=date.today, validators=[DataRequired()]); descricao = StringField('Descrição', validators=[DataRequired()]); forma_pagamento = SelectField('Forma de Pgto.', choices=[('', 'N/A'), ('Pix', 'Pix'), ('Transferência', 'Transferência'), ('Boleto', 'Boleto'), ('Cartão', 'Cartão')], validators=[Optional()]); recorrencia_switch = HiddenField(); recorrencia = SelectField('Repetir', choices=[('Mensal', 'Mensal'), ('Quinzenal', 'Quinzenal'), ('Anual', 'Anual')], validators=[Optional()]); data_final_recorrencia = DateField('Até (opcional)', validators=[Optional()]); submit = SubmitField('Salvar')

# --- FILTROS E FUNÇÕES DE AUXÍLIO ---
@app.template_filter('currency')
def format_currency(value):
    if value is None: return "R$ 0,00"
    return locale.currency(float(value), grouping=True, symbol='R$')
def get_db():
    if 'db' not in g:
        try:
            g.db = mysql.connector.connect(host=app.config['MYSQL_HOST'], user=app.config['MYSQL_USER'], password=app.config['MYSQL_PASSWORD'], database=app.config['MYSQL_DB'])
        except mysql.connector.Error as err:
            flash(f"Erro de conexão com o banco de dados: {err}", "danger"); return None
    return g.db
@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None: db.close()
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session: flash('Você precisa estar logado para ver esta página.', 'warning'); return redirect(url_for('login'))
        return view(**kwargs)
    return wrapped_view
def parse_currency(value_str):
    if not isinstance(value_str, str): return float(value_str)
    cleaned_value = value_str.replace('R$', '').strip().replace('.', '').replace(',', '.')
    return float(cleaned_value)
def expandir_transacoes_na_janela(regras, data_inicio_janela, data_fim_janela):
    transacoes_na_janela = []
    for t_row in regras:
        t = dict(t_row)
        data_regra = t['data']
        if not t['recorrencia']:
            if data_inicio_janela <= data_regra <= data_fim_janela:
                t['is_rule'] = True; transacoes_na_janela.append(t)
            continue
        data_corrente = data_regra
        data_final_regra = t['data_final_recorrencia'] or data_fim_janela
        if data_corrente > data_fim_janela: continue
        while data_corrente <= data_fim_janela and data_corrente <= data_final_regra:
            if data_corrente >= data_inicio_janela:
                nova_transacao = t.copy(); nova_transacao['data'] = data_corrente; nova_transacao['is_rule'] = (data_corrente == data_regra); transacoes_na_janela.append(nova_transacao)
            if data_corrente < data_regra: data_corrente = data_regra
            if t['recorrencia'] == 'Quinzenal': data_corrente += relativedelta(days=14)
            elif t['recorrencia'] == 'Mensal': data_corrente += relativedelta(months=1)
            elif t['recorrencia'] == 'Anual': data_corrente += relativedelta(years=1)
            else: break
            if t['data_final_recorrencia'] and data_corrente > data_final_regra: break
    return transacoes_na_janela

# --- ROTAS ---
@app.route('/login', methods=('GET', 'POST'))
def login():
    if 'user_id' in session: return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        db = get_db(); cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT * FROM usuarios WHERE username = %s', (form.username.data,)); user = cursor.fetchone(); cursor.close()
        if user is None or not check_password_hash(user['password'], form.password.data):
            flash('Nome de usuário ou senha incorretos.', 'danger')
        else:
            session.clear(); session['user_id'] = user['id']; session['username'] = user['username']; session['mostrar_saldos'] = bool(user['mostrar_saldos']); session['theme'] = user['theme']
            return redirect(url_for('index'))
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.clear(); flash('Você saiu da sua conta.', 'info'); return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    user_id = session['user_id']; db = get_db(); hoje = date.today(); form = TransacaoForm()
    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT id, nome, tipo FROM categorias WHERE user_id = %s ORDER BY nome', (user_id,)); user_categories = cursor.fetchall()
    cursor.execute("SELECT t.*, c.nome as categoria_nome FROM transacoes t JOIN categorias c ON t.categoria_id = c.id WHERE t.user_id = %s", (user_id,)); regras_transacoes = cursor.fetchall(); cursor.close()
    transacoes_ate_hoje = expandir_transacoes_na_janela(regras_transacoes, date(2000, 1, 1), hoje)
    saldo_atual = sum(t['valor'] if t['tipo'] == 'Receita' else -t['valor'] for t in transacoes_ate_hoje)
    inicio_mes_atual = hoje.replace(day=1); fim_mes_atual = inicio_mes_atual + relativedelta(months=1) - relativedelta(days=1)
    transacoes_mes_atual = [t for t in transacoes_ate_hoje if inicio_mes_atual <= t['data'] <= fim_mes_atual]
    receita_mes = sum(t['valor'] for t in transacoes_mes_atual if t['tipo'] == 'Receita')
    despesa_mes = sum(t['valor'] for t in transacoes_mes_atual if t['tipo'] == 'Despesa')
    despesas_mes_por_cat = {t['categoria_nome']: despesas_mes_por_cat.get(t['categoria_nome'], 0) + t['valor'] for t in transacoes_mes_atual if t['tipo'] == 'Despesa'}
    pie_chart_labels = list(despesas_mes_por_cat.keys()); pie_chart_valores = [float(v) for v in despesas_mes_por_cat.values()]
    bar_chart_labels = []; bar_chart_receitas = []; bar_chart_despesas = []
    for i in range(2, -1, -1):
        mes_ref = hoje - relativedelta(months=i); inicio_mes = mes_ref.replace(day=1); fim_mes = inicio_mes + relativedelta(months=1) - relativedelta(days=1)
        transacoes_do_mes = expandir_transacoes_na_janela(regras_transacoes, inicio_mes, fim_mes)
        bar_chart_labels.append(mes_ref.strftime('%b/%y').capitalize()); bar_chart_receitas.append(sum(t['valor'] for t in transacoes_do_mes if t['tipo'] == 'Receita')); bar_chart_despesas.append(sum(t['valor'] for t in transacoes_do_mes if t['tipo'] == 'Despesa'))
    transacoes_ate_hoje.sort(key=lambda x: (x['data'], x['id'] if isinstance(x['id'], int) else -1), reverse=True)
    return render_template('index.html', form=form, user_categories=user_categories, saldo_atual=saldo_atual, receita_mes=receita_mes, despesa_mes=despesa_mes,
        ultimas_10_transacoes=transacoes_ate_hoje[:10], pie_chart_labels=pie_chart_labels, pie_chart_valores=pie_chart_valores, bar_chart_labels=bar_chart_labels, 
        bar_chart_receitas=[float(v) for v in bar_chart_receitas], bar_chart_despesas=[float(v) for v in bar_chart_despesas], mostrar_saldos=session.get('mostrar_saldos', True))

@app.route('/toggle-saldo-visibility', methods=['POST'])
@login_required
def toggle_saldo_visibility():
    user_id = session['user_id']; nova_preferencia = not session.get('mostrar_saldos', True)
    db = get_db(); cursor = db.cursor(); cursor.execute('UPDATE usuarios SET mostrar_saldos = %s WHERE id = %s', (nova_preferencia, user_id)); db.commit(); cursor.close()
    session['mostrar_saldos'] = nova_preferencia; return jsonify(success=True)

@app.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    form = PerfilForm(); user_id = session['user_id']; db = get_db()
    cursor = db.cursor(dictionary=True); cursor.execute('SELECT * FROM usuarios WHERE id = %s', (user_id,)); user = cursor.fetchone(); cursor.close()
    if form.validate_on_submit():
        if not check_password_hash(user['password'], form.senha_atual.data):
            flash('A senha atual está incorreta para salvar as alterações.', 'danger')
        else:
            cursor = db.cursor()
            cursor.execute('UPDATE usuarios SET email = %s, theme = %s WHERE id = %s', (form.email.data, form.theme.data, user_id))
            session['theme'] = form.theme.data
            if form.nova_senha.data:
                cursor.execute('UPDATE usuarios SET password = %s WHERE id = %s', (generate_password_hash(form.nova_senha.data), user_id))
            db.commit(); cursor.close(); flash('Perfil atualizado com sucesso!', 'success'); return redirect(url_for('perfil'))
    form.email.data = user['email']; form.theme.data = user['theme']
    return render_template('perfil.html', form=form)

@app.route('/salvar-tema', methods=['POST'])
@login_required
def salvar_tema():
    novo_tema = request.json.get('theme')
    if novo_tema in ['light', 'dark', 'auto']:
        db = get_db(); cursor = db.cursor(); cursor.execute('UPDATE usuarios SET theme = %s WHERE id = %s', (novo_tema, session['user_id'])); db.commit(); cursor.close()
        session['theme'] = novo_tema
        return jsonify(success=True)
    return jsonify(success=False), 400

@app.route('/categorias/adicionar/ajax', methods=['POST'])
@login_required
def adicionar_categoria_ajax():
    form = CategoriaForm(data=request.json); db = get_db()
    if form.validate():
        cursor = db.cursor(dictionary=True); cursor.execute('SELECT id FROM categorias WHERE user_id = %s AND nome = %s', (session['user_id'], form.nome.data)); existente = cursor.fetchone()
        if existente: cursor.close(); return jsonify(success=False, errors={'nome': ['Uma categoria com este nome já existe.']})
        cursor.execute('INSERT INTO categorias (user_id, nome, tipo) VALUES (%s, %s, %s)',(session['user_id'], form.nome.data, form.tipo.data))
        new_id = cursor.lastrowid; db.commit(); cursor.close()
        return jsonify(success=True, categoria={'id': new_id, 'nome': form.nome.data, 'tipo': form.tipo.data})
    return jsonify(success=False, errors=form.errors)

@app.route('/transacoes')
@login_required
def transacoes_redirect():
    hoje = date.today(); return redirect(url_for('listar_transacoes', ano=hoje.year, mes=hoje.month))

@app.route('/transacoes/<int:ano>/<int:mes>')
@login_required
def listar_transacoes(ano, mes):
    db = get_db(); user_id = session['user_id']; form = TransacaoForm()
    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT id, nome, tipo FROM categorias WHERE user_id = %s ORDER BY nome', (user_id,)); user_categories = cursor.fetchall()
    cursor.execute("SELECT t.*, c.nome as categoria_nome FROM transacoes t JOIN categorias c ON t.categoria_id = c.id WHERE t.user_id = %s", (user_id,)); regras_transacoes = cursor.fetchall(); cursor.close()
    data_inicio_janela = date(ano, mes, 1); data_fim_janela = data_inicio_janela + relativedelta(months=1) - relativedelta(days=1)
    transacoes_do_mes = expandir_transacoes_na_janela(regras_transacoes, data_inicio_janela, data_fim_janela)
    transacoes_do_mes.sort(key=lambda x: (datetime.strptime(x['data'], '%Y-%m-%d') if isinstance(x['data'], str) else x['data'], x['id'] if isinstance(x['id'], int) else -1), reverse=True)
    data_atual = date(ano, mes, 1); mes_anterior = data_atual - relativedelta(months=1); mes_seguinte = data_atual + relativedelta(months=1)
    mes_display = data_atual.strftime('%B de %Y').capitalize()
    return render_template('transacoes.html', transacoes=transacoes_do_mes, form=form, user_categories=user_categories, nav_mes_display=mes_display, nav_mes_anterior=mes_anterior, nav_mes_seguinte=mes_seguinte)

@app.route('/transacoes/adicionar', methods=['POST'])
@login_required
def adicionar_transacao():
    form = TransacaoForm(); db = get_db(); user_id = session['user_id']
    cursor = db.cursor(); cursor.execute('SELECT id, nome FROM categorias WHERE user_id = %s ORDER BY nome', (user_id,)); form.categoria_id.choices = cursor.fetchall(); cursor.close()
    if form.validate_on_submit():
        valor = parse_currency(form.valor.data); recorrencia = form.recorrencia.data if form.recorrencia_switch.data == 'on' else None
        data_final = form.data_final_recorrencia.data if recorrencia else None
        cursor = db.cursor()
        cursor.execute('INSERT INTO transacoes (user_id, tipo, valor, categoria_id, data, descricao, recorrencia, data_final_recorrencia, forma_pagamento) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)',
            (user_id, form.tipo.data, valor, form.categoria_id.data, form.data.data, form.descricao.data, recorrencia, data_final, form.forma_pagamento.data))
        db.commit(); cursor.close(); flash('Transação adicionada!', 'success')
        data_transacao = form.data.data
        return redirect(url_for('listar_transacoes', ano=data_transacao.year, mes=data_transacao.month))
    else:
        for field, errors in form.errors.items(): flash(f"Erro no formulário: {errors[0]}", 'danger')
    return redirect(url_for('transacoes_redirect'))

@app.route('/transacoes/editar/<int:id>', methods=['POST'])
@login_required
def editar_transacao(id):
    form = TransacaoForm(); db = get_db(); user_id = session['user_id']
    cursor = db.cursor(); cursor.execute('SELECT id, nome FROM categorias WHERE user_id = %s ORDER BY nome', (user_id,)); form.categoria_id.choices = cursor.fetchall(); cursor.close()
    if form.validate_on_submit():
        valor = parse_currency(form.valor.data); recorrencia = form.recorrencia.data if form.recorrencia_switch.data == 'on' else None
        data_final = form.data_final_recorrencia.data if recorrencia else None
        cursor = db.cursor()
        cursor.execute('UPDATE transacoes SET tipo = %s, valor = %s, categoria_id = %s, data = %s, descricao = %s, recorrencia = %s, data_final_recorrencia = %s, forma_pagamento = %s WHERE id = %s AND user_id = %s',
            (form.tipo.data, valor, form.categoria_id.data, form.data.data, form.descricao.data, recorrencia, data_final, form.forma_pagamento.data, id, user_id))
        db.commit(); cursor.close(); flash('Transação atualizada!', 'success')
        data_transacao = form.data.data
        return redirect(url_for('listar_transacoes', ano=data_transacao.year, mes=data_transacao.month))
    else:
        for field, errors in form.errors.items(): flash(f"Erro no formulário: {errors[0]}", 'danger')
    return redirect(url_for('transacoes_redirect'))
    
@app.route('/transacoes/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_transacao(id):
    db = get_db(); cursor = db.cursor(); cursor.execute('DELETE FROM transacoes WHERE id = %s AND user_id = %s', (id, session['user_id'])); db.commit(); cursor.close()
    flash('Regra de transação excluída.', 'info'); return redirect(url_for('transacoes_redirect'))

@app.route('/categorias')
@login_required
def listar_categorias():
    form = CategoriaForm(); user_id = session['user_id']; db = get_db()
    cursor = db.cursor(dictionary=True); cursor.execute('SELECT * FROM categorias WHERE user_id = %s ORDER BY nome', (user_id,)); categorias = cursor.fetchall(); cursor.close()
    return render_template('categorias.html', categorias=categorias, form=form)

@app.route('/categorias/adicionar', methods=['POST',])
@login_required
def adicionar_categoria():
    form = CategoriaForm(); db = get_db()
    if form.validate_on_submit():
        cursor = db.cursor(dictionary=True); cursor.execute('SELECT id FROM categorias WHERE user_id = %s AND nome = %s', (session['user_id'], form.nome.data)); existente = cursor.fetchone()
        if existente: flash('Uma categoria com este nome já existe.', 'danger')
        else: cursor.execute('INSERT INTO categorias (user_id, nome, tipo) VALUES (%s, %s, %s)',(session['user_id'], form.nome.data, form.tipo.data)); db.commit(); flash('Categoria adicionada!', 'success')
        cursor.close()
    return redirect(url_for('listar_categorias'))

@app.route('/categorias/editar/<int:id>', methods=['POST',])
@login_required
def editar_categoria(id):
    form = CategoriaForm(); db = get_db()
    if form.validate_on_submit():
        cursor = db.cursor(dictionary=True); cursor.execute('SELECT id FROM categorias WHERE user_id = %s AND nome = %s AND id != %s', (session['user_id'], form.nome.data, id)); existente = cursor.fetchone()
        if existente: flash('Uma outra categoria já possui este nome.', 'danger')
        else: cursor.execute('UPDATE categorias SET nome = %s, tipo = %s WHERE id = %s AND user_id = %s',(form.nome.data, form.tipo.data, id, session['user_id'])); db.commit(); flash('Categoria atualizada!', 'success')
        cursor.close()
    return redirect(url_for('listar_categorias'))

@app.route('/categorias/excluir/<int:id>', methods=['POST',])
@login_required
def excluir_categoria(id):
    db = get_db(); cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT 1 FROM transacoes WHERE categoria_id = %s AND user_id = %s', (id, session['user_id'])); transacao_associada = cursor.fetchone()
    if transacao_associada: flash('Não é possível excluir. Categoria está em uso.', 'danger')
    else: cursor.execute('DELETE FROM categorias WHERE id = %s AND user_id = %s', (id, session['user_id'])); db.commit(); flash('Categoria excluída.', 'info')
    cursor.close()
    return redirect(url_for('listar_categorias'))

# --- ROTA DE ANÁLISES (ESTÁVEL) ---
@app.route('/analises')
@login_required
def analises():
    # Esta rota agora não tem parâmetros no caminho, apenas na query string
    user_id = session['user_id']; db = get_db(); hoje = date.today()
    cursor = db.cursor(dictionary=True)
    
    ano = request.args.get('ano', hoje.year, type=int)
    mes_str = request.args.get('mes')
    mes = int(mes_str) if mes_str and mes_str != '0' else None
    
    # Resto da lógica de análise...
    cursor.close()
    return render_template('analises.html', ...) # Retorna dados para o template

@cli.command("create-user")
@click.argument("username")
@click.argument("password")
@click.option("--email", default=None, help="O e-mail do usuário.")
def create_user(username, password, email):
    # Lógica de criação de usuário para MySQL
    try:
        db = mysql.connector.connect(host=app.config['MYSQL_HOST'], user=app.config['MYSQL_USER'], password=app.config['MYSQL_PASSWORD'], database=app.config['MYSQL_DB'])
        cursor = db.cursor()
    except mysql.connector.Error as err:
        print(f"Erro de conexão com o MySQL: {err}"); return
    
    # ... resto da lógica ...
    cursor.close(); db.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
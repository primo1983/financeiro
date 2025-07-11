from flask import render_template, redirect, url_for, jsonify, request, send_from_directory
from sqlalchemy.orm.attributes import flag_modified
from . import main_bp
from app import db
from app.models import Usuario, Transacao, Categoria
from app.forms import TransacaoForm
from app.utils import expandir_transacoes_na_janela, calcular_resumo_financeiro
from flask_login import login_required, current_user
from datetime import date
from dateutil.relativedelta import relativedelta

@main_bp.route('/')
@login_required
def index():
    user_id = current_user.id
    hoje = date.today()
    form = TransacaoForm()
    user_categories = Categoria.query.filter_by(user_id=user_id).order_by(Categoria.nome).all()
    
    regras_transacoes = Transacao.query.filter_by(user_id=user_id).options(db.joinedload(Transacao.categoria)).all()
    
    transacoes_ate_hoje = expandir_transacoes_na_janela(regras_transacoes, date(2000, 1, 1), hoje)
    resumo_total = calcular_resumo_financeiro(transacoes_ate_hoje)
    
    inicio_mes_atual = hoje.replace(day=1)
    fim_mes_atual = inicio_mes_atual + relativedelta(months=1) - relativedelta(days=1)
    transacoes_mes_atual = expandir_transacoes_na_janela(regras_transacoes, inicio_mes_atual, fim_mes_atual)
    resumo_mensal = calcular_resumo_financeiro(transacoes_mes_atual)
    
    transacoes_ate_hoje.sort(key=lambda x: (x['data'], x['id'] if isinstance(x['id'], int) else -1), reverse=True)

    visibilidade = current_user.saldos_visibilidade
    if visibilidade is None:
        visibilidade = {}

    return render_template('main/index.html', 
        form=form, 
        user_categories=user_categories, 
        saldo_atual=resumo_total['saldo'], 
        receita_mes=resumo_mensal['total_receitas'], 
        despesa_mes=resumo_mensal['total_despesas'], 
        saldo_mes=resumo_mensal['saldo'],
        ultimas_10_transacoes=transacoes_ate_hoje[:10],
        saldos_visibilidade=visibilidade
    )

@main_bp.route('/toggle-card-visibility', methods=['POST'])
@login_required
def toggle_card_visibility():
    card_name = request.json.get('card')
    if not card_name:
        return jsonify(success=False, error="Nome do card não fornecido."), 400

    user = db.session.get(Usuario, current_user.id)
    
    if not isinstance(user.saldos_visibilidade, dict):
        user.saldos_visibilidade = {
            "saldo_atual": True,
            "receita_mes": True,
            "despesa_mes": True,
            "saldo_mes": True
        }

    current_state = user.saldos_visibilidade.get(card_name, True)
    user.saldos_visibilidade[card_name] = not current_state
    
    flag_modified(user, 'saldos_visibilidade')
    db.session.commit()
    
    return jsonify(success=True, card=card_name, newState=(not current_state))

# Rota para servir o Service Worker com o cabeçalho de permissão correto
@main_bp.route('/sw.js')
def service_worker():
    response = send_from_directory('static', 'sw.js')
    response.headers['Service-Worker-Allowed'] = '/'
    return response
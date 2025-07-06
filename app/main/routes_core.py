from flask import render_template, redirect, url_for, jsonify
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
    saldo_atual = resumo_total['saldo']
    
    inicio_mes_atual = hoje.replace(day=1)
    fim_mes_atual = inicio_mes_atual + relativedelta(months=1) - relativedelta(days=1)
    transacoes_mes_atual = expandir_transacoes_na_janela(regras_transacoes, inicio_mes_atual, fim_mes_atual)
    resumo_mensal = calcular_resumo_financeiro(transacoes_mes_atual)
    
    # Prepara a lista de receitas para o novo card
    receitas_previstas_lista = [t for t in transacoes_mes_atual if t['tipo'] == 'Receita' and not t.get('is_skipped')]
    
    # Cálculo para o Saldo Previsto (considera tudo, mesmo pulados)
    receitas_previstas_total = sum(t['valor'] for t in transacoes_mes_atual if t['tipo'] == 'Receita')
    despesas_previstas_total = sum(t['valor'] for t in transacoes_mes_atual if t['tipo'] == 'Despesa')
    saldo_previsto = receitas_previstas_total - despesas_previstas_total
    
    transacoes_ate_hoje.sort(key=lambda x: (x['data'], x['id'] if isinstance(x['id'], int) else -1), reverse=True)

    return render_template('main/index.html', form=form, user_categories=user_categories, 
        saldo_atual=saldo_atual, 
        receita_mes=resumo_mensal['total_receitas'], 
        despesa_mes=resumo_mensal['total_despesas'], 
        saldo_mes=resumo_mensal['saldo'],
        saldo_previsto=saldo_previsto,
        ultimas_10_transacoes=transacoes_ate_hoje[:10],
        receitas_previstas_lista=receitas_previstas_lista,
        # CORREÇÃO: Passando as variáveis do gráfico de pizza de volta para o template
        pie_chart_labels=list(resumo_mensal['despesas_por_categoria'].keys()),
        pie_chart_valores=[float(v) for v in resumo_mensal['despesas_por_categoria'].values()],
        mostrar_saldos=current_user.mostrar_saldos
    )

@main_bp.route('/toggle-saldo-visibility', methods=['POST'])
@login_required
def toggle_saldo_visibility():
    user = db.session.get(Usuario, current_user.id)
    user.mostrar_saldos = not user.mostrar_saldos
    db.session.commit()
    return jsonify(success=True)
from flask import render_template, redirect, url_for, jsonify, flash
from . import main_bp
from app import db
from app.models import Usuario, Transacao, Categoria
from app.forms import TransacaoForm
from app.utils import expandir_transacoes_na_janela, calcular_resumo_financeiro
from flask_login import login_required, current_user
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal

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
    
    # Cálculos para o que foi realizado (ignorando transações puladas)
    resumo_mensal_realizado = calcular_resumo_financeiro(transacoes_mes_atual)
    
    # NOVO CÁLCULO: Saldo Previsto (considera tudo, mesmo o que foi pulado)
    receitas_previstas = sum(t['valor'] for t in transacoes_mes_atual if t['tipo'] == 'Receita')
    despesas_previstas = sum(t['valor'] for t in transacoes_mes_atual if t['tipo'] == 'Despesa')
    saldo_previsto = receitas_previstas - despesas_previstas

    # Gráfico de pizza continua baseado no que foi realizado
    despesas_por_cat = resumo_mensal_realizado['despesas_por_categoria']
    pie_chart_labels = list(despesas_por_cat.keys())
    pie_chart_valores = [float(v) for v in despesas_por_cat.values()]
    
    bar_chart_labels = []
    bar_chart_receitas = []
    bar_chart_despesas = []
    for i in range(2, -1, -1):
        mes_ref = hoje - relativedelta(months=i)
        inicio_mes = mes_ref.replace(day=1); fim_mes = inicio_mes + relativedelta(months=1) - relativedelta(days=1)
        transacoes_do_mes = expandir_transacoes_na_janela(regras_transacoes, inicio_mes, fim_mes)
        resumo_barra = calcular_resumo_financeiro(transacoes_do_mes)
        bar_chart_labels.append(mes_ref.strftime('%b/%y').capitalize())
        bar_chart_receitas.append(resumo_barra['total_receitas'])
        bar_chart_despesas.append(resumo_barra['total_despesas'])
        
    transacoes_ate_hoje.sort(key=lambda x: (x['data'], x['id'] if isinstance(x['id'], int) else -1), reverse=True)

    return render_template('main/index.html', form=form, user_categories=user_categories, 
        saldo_atual=saldo_atual, 
        receita_mes=resumo_mensal_realizado['total_receitas'], 
        despesa_mes=resumo_mensal_realizado['total_despesas'], 
        saldo_mes=resumo_mensal_realizado['saldo'],
        saldo_previsto=saldo_previsto, # Passando a nova variável
        ultimas_10_transacoes=transacoes_ate_hoje[:10], 
        pie_chart_labels=pie_chart_labels, 
        pie_chart_valores=pie_chart_valores, 
        bar_chart_labels=bar_chart_labels, 
        bar_chart_receitas=bar_chart_receitas, 
        bar_chart_despesas=bar_chart_despesas, 
        mostrar_saldos=current_user.mostrar_saldos
    )

@main_bp.route('/toggle-saldo-visibility', methods=['POST'])
@login_required
def toggle_saldo_visibility():
    user = db.session.get(Usuario, current_user.id)
    user.mostrar_saldos = not user.mostrar_saldos
    db.session.commit()
    return jsonify(success=True)
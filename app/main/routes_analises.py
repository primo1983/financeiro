from flask import render_template, request, redirect, url_for, Response, flash
from . import main_bp
from app import db
from app.models import Categoria, Transacao
from app.utils import expandir_transacoes_na_janela, calcular_resumo_financeiro
from flask_login import login_required, current_user
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import io, csv

def get_transacoes_filtradas_analise(user_id, data_inicio, data_fim):
    """Função auxiliar para buscar e filtrar transações para um período específico."""
    tipo_filtro = request.args.get('tipo', 'Todos')
    categorias_filtro_ids_str = request.args.getlist('categoria')

    regras_transacoes = Transacao.query.filter_by(user_id=user_id).options(db.joinedload(Transacao.categoria)).all()
    transacoes_no_periodo = expandir_transacoes_na_janela(regras_transacoes, data_inicio, data_fim)
    
    transacoes_filtradas = [t for t in transacoes_no_periodo if not t.get('is_skipped')]
    
    if tipo_filtro in ['Receita', 'Despesa']:
        transacoes_filtradas = [t for t in transacoes_filtradas if t['tipo'] == tipo_filtro]
    
    categorias_filtro_ids = [int(id) for id in categorias_filtro_ids_str] if categorias_filtro_ids_str else []
    if categorias_filtro_ids:
        transacoes_filtradas = [t for t in transacoes_filtradas if t['categoria_id'] in categorias_filtro_ids]

    return transacoes_filtradas, tipo_filtro, categorias_filtro_ids

@main_bp.route('/analises')
@login_required
def analises_redirect():
    """Redireciona para a página de análises do mês atual."""
    hoje = date.today()
    return redirect(url_for('main.analises', ano=hoje.year, mes=hoje.month))

@main_bp.route('/analises/<int:ano>/<int:mes>')
@login_required
def analises(ano, mes):
    user_id = current_user.id
    data_inicio = date(ano, mes, 1)
    data_fim = data_inicio + relativedelta(months=1) - relativedelta(days=1)
    
    transacoes_filtradas, tipo_filtro, categorias_filtro_ids = get_transacoes_filtradas_analise(user_id, data_inicio, data_fim)
    
    resumo_periodo = calcular_resumo_financeiro(transacoes_filtradas)
    
    todas_as_categorias_usuario = Categoria.query.filter_by(user_id=user_id).order_by(Categoria.nome).all()

    return render_template('main/analises.html', 
        data_inicio=data_inicio.strftime('%Y-%m-%d'), 
        data_fim=data_fim.strftime('%Y-%m-%d'),
        ano_selecionado=ano, 
        mes_selecionado=mes,
        tipo_filtro=tipo_filtro, 
        categorias_filtro_ids=categorias_filtro_ids,
        todas_as_categorias_usuario=todas_as_categorias_usuario,
        total_receitas=resumo_periodo['total_receitas'], 
        total_despesas=resumo_periodo['total_despesas'],
        saldo_periodo=resumo_periodo['saldo'],
        grafico_despesas_labels=list(resumo_periodo['despesas_por_categoria'].keys()), 
        grafico_despesas_valores=[float(v) for v in resumo_periodo['despesas_por_categoria'].values()],
        grafico_receitas_labels=list(resumo_periodo['receitas_por_categoria'].keys()), 
        grafico_receitas_valores=[float(v) for v in resumo_periodo['receitas_por_categoria'].values()]
    )

@main_bp.route('/exportar/csv')
@login_required
def exportar_csv():
    user_id = current_user.id
    start_str = request.args.get('inicio')
    end_str = request.args.get('fim')
    
    try:
        data_inicio = datetime.strptime(start_str, '%Y-%m-%d').date()
        data_fim = datetime.strptime(end_str, '%Y-%m-%d').date()
    except:
        hoje = date.today()
        data_inicio = hoje.replace(day=1)
        data_fim = data_inicio + relativedelta(months=1) - relativedelta(days=1)

    transacoes_filtradas, _, _ = get_transacoes_filtradas_analise(user_id, data_inicio, data_fim)
    
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')
    writer.writerow(['Data', 'Descrição', 'Valor', 'Tipo', 'Categoria', 'Forma de Pagamento'])
    for t in sorted(transacoes_filtradas, key=lambda x: x['data']):
        valor_formatado = f"{t['valor']:.2f}".replace('.', ',')
        writer.writerow([t['data'].strftime('%d/%m/%Y'), t['descricao'], valor_formatado, t['tipo'], t['categoria_nome'], t.get('forma_pagamento', '')])
    output.seek(0)
    filename = f"relatorio_{data_inicio.strftime('%Y-%m-%d')}_a_{data_fim.strftime('%Y-%m-%d')}.csv"
    return Response(output, mimetype="text/csv", headers={"Content-Disposition": f"attachment;filename={filename}"})
from flask import render_template, request, redirect, url_for, Response, flash
from . import main_bp
from app import db
from app.models import Categoria, Transacao
from app.utils import expandir_transacoes_na_janela, calcular_resumo_financeiro
from flask_login import login_required, current_user
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import io, csv

def get_transacoes_filtradas_analise(user_id):
    hoje = date.today()
    start_str = request.args.get('inicio', hoje.replace(day=1).strftime('%Y-%m-%d'))
    end_str = request.args.get('fim', (hoje.replace(day=1) + relativedelta(months=1) - relativedelta(days=1)).strftime('%Y-%m-%d'))
    try: data_inicio = datetime.strptime(start_str, '%Y-%m-%d').date(); data_fim = datetime.strptime(end_str, '%Y-%m-%d').date()
    except (ValueError, TypeError): data_inicio = hoje.replace(day=1); data_fim = data_inicio + relativedelta(months=1) - relativedelta(days=1); start_str = data_inicio.strftime('%Y-%m-%d'); end_str = data_fim.strftime('%Y-%m-%d')
    tipo_filtro = request.args.get('tipo', 'Todos'); categorias_filtro_ids_str = request.args.getlist('categoria')
    regras_transacoes = Transacao.query.filter_by(user_id=user_id).options(db.joinedload(Transacao.categoria)).all()
    transacoes_no_periodo = expandir_transacoes_na_janela(regras_transacoes, data_inicio, data_fim)
    transacoes_filtradas = [t for t in transacoes_no_periodo if not t.get('is_skipped')]
    if tipo_filtro in ['Receita', 'Despesa']:
        transacoes_filtradas = [t for t in transacoes_filtradas if t['tipo'] == tipo_filtro]
    categorias_filtro_ids = [int(id) for id in categorias_filtro_ids_str] if categorias_filtro_ids_str else []
    if categorias_filtro_ids:
        transacoes_filtradas = [t for t in transacoes_filtradas if t['categoria_id'] in categorias_filtro_ids]
    return transacoes_filtradas, tipo_filtro, categorias_filtro_ids, start_str, end_str, data_inicio.year, mes if (mes := (data_inicio.month if data_inicio.day == 1 else None)) else None

@main_bp.route('/analises-redirect')
@login_required
def analises_redirect():
    hoje = date.today()
    return redirect(url_for('main.analises', ano=hoje.year, mes=hoje.month))

@main_bp.route('/analises/<int:ano>/<int:mes>')
@login_required
def analises(ano, mes):
    user_id = current_user.id
    # A lógica de filtro agora é mais simples
    transacoes_filtradas, tipo_filtro, categorias_filtro_ids, start_str, end_str = get_transacoes_filtradas_analise(user_id)
    resumo_periodo = calcular_resumo_financeiro(transacoes_filtradas)
    todas_as_categorias_usuario = Categoria.query.filter_by(user_id=user_id).order_by(Categoria.nome).all()
    return render_template('main/analises.html', 
        data_inicio=start_str, data_fim=end_str,
        ano_selecionado=ano, mes_selecionado=mes,
        tipo_filtro=tipo_filtro, categorias_filtro_ids=categorias_filtro_ids,
        todas_as_categorias_usuario=todas_as_categorias_usuario,
        total_receitas=resumo_periodo['total_receitas'], total_despesas=resumo_periodo['total_despesas'],
        saldo_periodo=resumo_periodo['saldo'],
        grafico_despesas_labels=list(resumo_periodo['despesas_por_categoria'].keys()), 
        grafico_despesas_valores=[float(v) for v in resumo_periodo['despesas_por_categoria'].values()],
        grafico_receitas_labels=list(resumo_periodo['receitas_por_categoria'].keys()), 
        grafico_receitas_valores=[float(v) for v in resumo_periodo['receitas_por_categoria'].values()])

@main_bp.route('/exportar/csv')
@login_required
def exportar_csv():
    user_id = current_user.id
    transacoes_filtradas, _, _, start_str, end_str = get_transacoes_filtradas_analise(user_id)
    output = io.StringIO(); writer = csv.writer(output, delimiter=';')
    writer.writerow(['Data', 'Descrição', 'Valor', 'Tipo', 'Categoria', 'Forma de Pagamento'])
    for t in sorted(transacoes_filtradas, key=lambda x: x['data']):
        valor_formatado = f"{t['valor']:.2f}".replace('.', ',')
        writer.writerow([t['data'].strftime('%d/%m/%Y'), t['descricao'], valor_formatado, t['tipo'], t['categoria_nome'], t.get('forma_pagamento', '')])
    output.seek(0)
    filename = f"relatorio_{start_str}_a_{end_str}.csv"
    return Response(output, mimetype="text/csv", headers={"Content-Disposition": f"attachment;filename={filename}"})
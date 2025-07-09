from flask import render_template, request, redirect, url_for, Response, flash, jsonify
from . import main_bp
from app import db
from app.models import Categoria, Transacao
from app.utils import expandir_transacoes_na_janela, calcular_resumo_financeiro
from flask_login import login_required, current_user
from sqlalchemy import func
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import io, csv

def get_transacoes_filtradas_analise(user_id, data_inicio, data_fim):
    """Função auxiliar para buscar e filtrar transações para um período específico."""
    tipo_filtro = request.args.get('tipo', 'Todos')
    categorias_filtro_ids_str = request.args.getlist('categoria')
    search_term = request.args.get('q', '').strip()

    query = Transacao.query.filter_by(user_id=user_id).options(db.joinedload(Transacao.categoria))
    if search_term:
        query = query.filter(Transacao.descricao.ilike(f'%{search_term}%'))
    
    regras_transacoes = query.all()
    transacoes_no_periodo = expandir_transacoes_na_janela(regras_transacoes, data_inicio, data_fim)
    
    transacoes_filtradas = [t for t in transacoes_no_periodo if not t.get('is_skipped')]
    
    if tipo_filtro in ['Receita', 'Despesa']:
        transacoes_filtradas = [t for t in transacoes_filtradas if t['tipo'] == tipo_filtro]
    
    if categorias_filtro_ids_str:
        try:
            categorias_filtro_ids = [int(id_str) for id_str in categorias_filtro_ids_str if id_str]
            if categorias_filtro_ids:
                transacoes_filtradas = [t for t in transacoes_filtradas if t['categoria_id'] in categorias_filtro_ids]
        except ValueError:
            flash('ID de categoria inválido recebido.', 'warning')

    return transacoes_filtradas, tipo_filtro, categorias_filtro_ids_str, search_term

@main_bp.route('/analises')
@login_required
def analises_redirect():
    hoje = date.today()
    data_inicio = hoje.replace(day=1)
    data_fim = data_inicio + relativedelta(months=1) - relativedelta(days=1)
    return redirect(url_for('main.analises', inicio=data_inicio.strftime('%Y-%m-%d'), fim=data_fim.strftime('%Y-%m-%d')))

@main_bp.route('/analises/view')
@login_required
def analises():
    user_id = current_user.id
    try:
        data_inicio = datetime.strptime(request.args.get('inicio'), '%Y-%m-%d').date()
        data_fim = datetime.strptime(request.args.get('fim'), '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return redirect(url_for('main.analises_redirect'))

    transacoes_filtradas, tipo_filtro, categorias_filtro_ids, search_term = get_transacoes_filtradas_analise(user_id, data_inicio, data_fim)
    resumo_periodo = calcular_resumo_financeiro(transacoes_filtradas)
    todas_as_categorias_usuario = Categoria.query.filter_by(user_id=user_id).order_by(Categoria.nome).all()

    transacoes_filtradas.sort(key=lambda x: x['data'], reverse=True)

    return render_template('main/analises.html', 
        transacoes=transacoes_filtradas, 
        data_inicio=data_inicio.strftime('%Y-%m-%d'), data_fim=data_fim.strftime('%Y-%m-%d'),
        tipo_filtro=tipo_filtro, categorias_filtro_ids=[int(id) for id in categorias_filtro_ids if id],
        search_term=search_term,
        todas_as_categorias_usuario=todas_as_categorias_usuario,
        total_receitas=resumo_periodo['total_receitas'], total_despesas=resumo_periodo['total_despesas'],
        saldo_periodo=resumo_periodo['saldo']
        # Linhas dos gráficos de pizza foram removidas daqui
    )

@main_bp.route('/exportar/csv')
@login_required
def exportar_csv():
    # ... (código da função continua igual) ...
    user_id = current_user.id
    start_str = request.args.get('inicio'); end_str = request.args.get('fim')
    try:
        data_inicio = datetime.strptime(start_str, '%Y-%m-%d').date()
        data_fim = datetime.strptime(end_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        hoje = date.today()
        data_inicio = hoje.replace(day=1)
        data_fim = data_inicio + relativedelta(months=1) - relativedelta(days=1)

    transacoes_filtradas, _, _, _ = get_transacoes_filtradas_analise(user_id, data_inicio, data_fim)
    
    output = io.StringIO(); writer = csv.writer(output, delimiter=';')
    writer.writerow(['Data', 'Descrição', 'Valor', 'Tipo', 'Categoria', 'Forma de Pagamento'])
    for t in sorted(transacoes_filtradas, key=lambda x: x['data']):
        valor_formatado = f"{t['valor']:.2f}".replace('.', ',')
        writer.writerow([t['data'].strftime('%d/%m/%Y'), t['descricao'], valor_formatado, t['tipo'], t['categoria_nome'], t.get('forma_pagamento', '')])
    output.seek(0)
    filename = f"relatorio_{data_inicio.strftime('%Y-%m-%d')}_a_{data_fim.strftime('%Y-%m-%d')}.csv"
    return Response(output, mimetype="text/csv", headers={"Content-Disposition": f"attachment;filename={filename}"})


@main_bp.route('/api/analises')
@login_required
def get_dados_analise():
    """Endpoint de API que retorna os dados de análise em formato JSON."""
    try:
        data_inicio = datetime.strptime(request.args.get('inicio'), '%Y-%m-%d').date()
        data_fim = datetime.strptime(request.args.get('fim'), '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return jsonify(success=False, error="Datas inválidas ou não fornecidas."), 400

    transacoes_filtradas, _, _, _ = get_transacoes_filtradas_analise(current_user.id, data_inicio, data_fim)
    resumo_periodo = calcular_resumo_financeiro(transacoes_filtradas)
    
    transacoes_json = []
    for t in transacoes_filtradas:
        transacoes_json.append({
            'data': t['data'].strftime('%d/%m/%Y'), 'tipo': t['tipo'],
            'tipo_badge_class': 'text-bg-success' if t['tipo'] == 'Receita' else 'text-bg-danger',
            'categoria_nome': t['categoria_nome'], 'descricao': t['descricao'],
            'valor': float(t['valor']),
            'valor_class': 'text-success' if t['tipo'] == 'Receita' else 'text-danger'
        })
    transacoes_json.sort(key=lambda x: datetime.strptime(x['data'], '%d/%m/%Y'), reverse=True)
    
    return jsonify(
        success=True,
        total_receitas=float(resumo_periodo['total_receitas']),
        total_despesas=float(resumo_periodo['total_despesas']),
        saldo_periodo=float(resumo_periodo['saldo']),
        transacoes=transacoes_json
        # Chaves dos gráficos de pizza foram removidas daqui
    )
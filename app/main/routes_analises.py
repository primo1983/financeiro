from flask import render_template, request, redirect, url_for, Response, flash, jsonify
from . import main_bp
from app import db
from app.models import Categoria, Transacao
from app.utils import expandir_transacoes_na_janela, calcular_resumo_financeiro, get_transacoes_filtradas_analise, format_currency
from flask_login import login_required, current_user
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import io, csv

# ... (o início do arquivo, com get_transacoes_filtradas_analise, analises_redirect, etc., continua igual)
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

    query_regras = get_transacoes_filtradas_analise(user_id)
    transacoes_filtradas = expandir_transacoes_na_janela(query_regras.all(), data_inicio, data_fim)
    
    resumo_periodo = calcular_resumo_financeiro(transacoes_filtradas)
    todas_as_categorias_usuario = Categoria.query.filter_by(user_id=user_id).order_by(Categoria.nome).all()
    transacoes_filtradas.sort(key=lambda x: x['data'], reverse=True)

    tipo_filtro = request.args.get('tipo', 'Todos')
    categorias_filtro_ids_str = request.args.getlist('categoria')
    search_term = request.args.get('q', '')

    return render_template('main/analises.html', 
        transacoes=transacoes_filtradas, 
        data_inicio=data_inicio.strftime('%Y-%m-%d'), data_fim=data_fim.strftime('%Y-%m-%d'),
        tipo_filtro=tipo_filtro, categorias_filtro_ids=[int(id) for id in categorias_filtro_ids_str if id],
        search_term=search_term,
        user_categories=todas_as_categorias_usuario,
        total_receitas=resumo_periodo['total_receitas'], total_despesas=resumo_periodo['total_despesas'],
        saldo_periodo=resumo_periodo['saldo']
    )

@main_bp.route('/exportar/csv')
@login_required
def exportar_csv():
    user_id = current_user.id
    start_str = request.args.get('inicio'); end_str = request.args.get('fim')
    try:
        data_inicio = datetime.strptime(start_str, '%Y-%m-%d').date()
        data_fim = datetime.strptime(end_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        hoje = date.today()
        data_inicio = hoje.replace(day=1)
        data_fim = data_inicio + relativedelta(months=1) - relativedelta(days=1)

    query_regras = get_transacoes_filtradas_analise(user_id)
    transacoes_filtradas = expandir_transacoes_na_janela(query_regras.all(), data_inicio, data_fim)
    
    output = io.StringIO(); writer = csv.writer(output, delimiter=';')
    writer.writerow(['Data', 'Descrição', 'Valor', 'Tipo', 'Categoria', 'Forma de Pagamento'])
    for t in sorted(transacoes_filtradas, key=lambda x: x['data']):
        valor_formatado = f"{t['valor']:.2f}".replace('.', ',')
        writer.writerow([t['data'].strftime('%d/%m/%Y'), t['descricao'], valor_formatado, t['tipo'], t['categoria_nome'], t.get('forma_pagamento', '')])
    output.seek(0)
    filename = f"relatorio_{data_inicio.strftime('%Y-%m-%d')}_a_{data_fim.strftime('%Y-%m-%d')}.csv"
    return Response(output, mimetype="text/csv", headers={"Content-Disposition": f"attachment;filename={filename}"})


# --- ROTA DE API CORRIGIDA ---
@main_bp.route('/api/analises')
@login_required
def get_dados_analise():
    try:
        data_inicio = datetime.strptime(request.args.get('inicio'), '%Y-%m-%d').date()
        data_fim = datetime.strptime(request.args.get('fim'), '%Y-%m-%d').date()
        page = request.args.get('page', 1, type=int) # Adicionado para consistência
        per_page = 20
    except (ValueError, TypeError):
        return jsonify(success=False, error="Datas inválidas ou não fornecidas."), 400

    query_regras = get_transacoes_filtradas_analise(current_user.id)
    transacoes_filtradas = expandir_transacoes_na_janela(query_regras.all(), data_inicio, data_fim)
    
    resumo_periodo = calcular_resumo_financeiro(transacoes_filtradas)
    
    transacoes_filtradas.sort(key=lambda x: x['data'], reverse=True)

    # Lógica de paginação manual (igual à da pág. de transações)
    total_items = len(transacoes_filtradas)
    total_pages = (total_items + per_page - 1) // per_page if per_page > 0 else 0
    start = (page - 1) * per_page
    end = start + per_page
    transacoes_paginadas = transacoes_filtradas[start:end]
    
    transacoes_json = []
    for t in transacoes_paginadas:
        transacoes_json.append({
            'data_formatada': t['data'].strftime('%d/%m/%Y'), # Enviando com o nome correto
            'tipo': t['tipo'],
            'tipo_badge_class': 'text-bg-success' if t['tipo'] == 'Receita' else 'text-bg-danger',
            'categoria_nome': t['categoria_nome'], 
            'descricao': t['descricao'],
            'valor_formatado': format_currency(t['valor']), # Enviando com o nome correto
            'valor_class': 'text-success' if t['tipo'] == 'Receita' else 'text-danger'
        })
    
    return jsonify(
        success=True,
        # Enviando os valores dos cards já formatados
        total_receitas=format_currency(resumo_periodo['total_receitas']),
        total_despesas=format_currency(resumo_periodo['total_despesas']),
        saldo_periodo=format_currency(resumo_periodo['saldo']),
        transacoes=transacoes_json,
        has_next=(page < total_pages),
        has_prev=(page > 1),
        next_page=(page + 1 if page < total_pages else None),
        prev_page=(page - 1 if page > 1 else None),
        current_page=page,
        total_pages=total_pages
    )
import locale
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from flask import request, flash
from app.models import ExcecaoTransacao, Transacao, Categoria
from sqlalchemy import func, and_
from app import db
from flask_login import current_user

def format_currency(value):
    if value is None: return "R$ 0,00"
    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
        except locale.Error:
            return f"R$ {value:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")
    return locale.currency(float(value), grouping=True, symbol='R$')

def parse_currency(value_str):
    if not isinstance(value_str, str): return float(value_str)
    cleaned_value = value_str.replace('R$', '').strip().replace('.', '').replace(',', '.')
    return float(cleaned_value)

def expandir_transacoes_na_janela(regras, data_inicio_janela, data_fim_janela):
    if not current_user.is_authenticated: return []
    transacoes_na_janela = []
    excecoes = ExcecaoTransacao.query.filter_by(user_id=current_user.id).all()
    excecoes_set = {(e.transacao_id, e.data_excecao) for e in excecoes}
    for t in regras:
        data_regra = t.data
        if not t.recorrencia:
            if data_inicio_janela <= data_regra <= data_fim_janela:
                transacoes_na_janela.append({ 'id': t.id, 'descricao': t.descricao, 'valor': float(t.valor), 'data': t.data, 'tipo': t.tipo, 'categoria_id': t.categoria_id, 'forma_pagamento': t.forma_pagamento, 'recorrencia': t.recorrencia, 'data_final_recorrencia': t.data_final_recorrencia, 'is_rule': True, 'categoria_nome': t.categoria.nome if t.categoria else 'Sem Categoria', 'is_skipped': False })
            continue
        data_corrente = data_regra
        data_final_regra = t.data_final_recorrencia or data_fim_janela
        if data_corrente > data_fim_janela: continue
        while data_corrente <= data_final_regra:
            if data_corrente > data_fim_janela: break
            if data_corrente >= data_inicio_janela:
                is_exception = (t.id, data_corrente) in excecoes_set
                transacoes_na_janela.append({ 'id': t.id, 'descricao': t.descricao, 'valor': float(t.valor), 'data': data_corrente, 'tipo': t.tipo, 'categoria_id': t.categoria_id, 'forma_pagamento': t.forma_pagamento, 'recorrencia': t.recorrencia, 'data_final_recorrencia': t.data_final_recorrencia, 'is_rule': (data_corrente == data_regra), 'categoria_nome': t.categoria.nome if t.categoria else 'Sem Categoria', 'is_skipped': is_exception })
            if data_corrente < data_regra: data_corrente = data_regra
            if t.recorrencia == 'Quinzenal': data_corrente += relativedelta(days=14)
            elif t.recorrencia == 'Mensal': data_corrente += relativedelta(months=1)
            elif t.recorrencia == 'Anual': data_corrente += relativedelta(years=1)
            else: break
            if t.data_final_recorrencia and data_corrente > data_final_regra: break
    return transacoes_na_janela

def calcular_resumo_financeiro(lista_transacoes):
    transacoes_validas = [t for t in lista_transacoes if not t.get('is_skipped')]
    total_receitas = sum(t['valor'] for t in transacoes_validas if t['tipo'] == 'Receita')
    total_despesas = sum(t['valor'] for t in transacoes_validas if t['tipo'] == 'Despesa')
    receitas_por_cat = {}; despesas_por_cat = {}
    for t in transacoes_validas:
        cat_nome = t.get('categoria_nome', 'Sem Categoria')
        if t['tipo'] == 'Receita':
            receitas_por_cat[cat_nome] = receitas_por_cat.get(cat_nome, 0) + t['valor']
        else:
            despesas_por_cat[cat_nome] = despesas_por_cat.get(cat_nome, 0) + t['valor']
    return {"total_receitas": total_receitas, "total_despesas": total_despesas, "saldo": total_receitas - total_despesas, "receitas_por_categoria": receitas_por_cat, "despesas_por_categoria": despesas_por_cat}

def get_transacoes_filtradas_analise(user_id):
    """Função auxiliar que monta a query inicial de transações com base nos filtros da request."""
    tipo_filtro = request.args.get('tipo', 'Todos')
    categorias_filtro_ids_str = request.args.getlist('categoria')
    search_term = request.args.get('q', '').strip()
    query = Transacao.query.filter_by(user_id=user_id).options(db.joinedload(Transacao.categoria))
    if search_term:
        query = query.filter(Transacao.descricao.ilike(f'%{search_term}%'))
    if tipo_filtro in ['Receita', 'Despesa']:
        query = query.filter(Transacao.tipo == tipo_filtro)
    if categorias_filtro_ids_str:
        try:
            categorias_filtro_ids = [int(id_str) for id_str in categorias_filtro_ids_str if id_str]
            if categorias_filtro_ids:
                query = query.filter(Transacao.categoria_id.in_(categorias_filtro_ids))
        except ValueError:
            flash('ID de categoria inválido recebido.', 'warning')
    return query
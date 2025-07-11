from flask import render_template, request, redirect, url_for, flash, jsonify
from . import main_bp
from app import db
from app.models import Transacao, Categoria, ExcecaoTransacao
from app.forms import TransacaoForm
from app.utils import expandir_transacoes_na_janela, parse_currency, get_transacoes_filtradas_analise, format_currency
from flask_login import login_required, current_user
from flask_wtf.csrf import generate_csrf
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

@main_bp.route('/transacoes')
@login_required
def transacoes_redirect():
    hoje = date.today()
    data_inicio = hoje.replace(day=1)
    data_fim = data_inicio + relativedelta(months=1) - relativedelta(days=1)
    return redirect(url_for('main.listar_transacoes', inicio=data_inicio.strftime('%Y-%m-%d'), fim=data_fim.strftime('%Y-%m-%d')))

@main_bp.route('/transacoes/view')
@login_required
def listar_transacoes():
    try:
        data_inicio = datetime.strptime(request.args.get('inicio'), '%Y-%m-%d').date()
        data_fim = datetime.strptime(request.args.get('fim'), '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return redirect(url_for('main.transacoes_redirect'))
        
    todas_as_categorias_usuario = Categoria.query.filter_by(user_id=current_user.id).order_by(Categoria.nome).all()
    form = TransacaoForm()

    return render_template('main/transacoes.html', 
        data_inicio=data_inicio.strftime('%Y-%m-%d'), 
        data_fim=data_fim.strftime('%Y-%m-%d'),
        user_categories=todas_as_categorias_usuario,
        form=form
    )

@main_bp.route('/api/transacoes')
@login_required
def get_dados_transacoes():
    try:
        data_inicio = datetime.strptime(request.args.get('inicio'), '%Y-%m-%d').date()
        data_fim = datetime.strptime(request.args.get('fim'), '%Y-%m-%d').date()
        page = request.args.get('page', 1, type=int)
        per_page = 20
        sort_by = request.args.get('sort_by', 'data')
        order = request.args.get('order', 'desc')
    except (ValueError, TypeError):
        return jsonify(success=False, error="Parâmetros inválidos."), 400

    query_regras = get_transacoes_filtradas_analise(current_user.id)
    regras_filtradas = query_regras.all()
    
    transacoes_expandidas = expandir_transacoes_na_janela(regras_filtradas, data_inicio, data_fim)
    
    # --- LÓGICA DE ORDENAÇÃO APLICADA AQUI ---
    # Mapeia os nomes das colunas para chaves seguras e tipos corretos
    key_map = {
        'categoria_nome': lambda t: (t.get('categoria_nome') or '').lower(),
        'tipo': lambda t: (t.get('tipo') or '').lower(),
        'descricao': lambda t: (t.get('descricao') or '').lower(),
        'data': lambda t: t.get('data', date.min),
        'valor': lambda t: t.get('valor', 0.0)
    }
    sort_key_func = key_map.get(sort_by, key_map['data'])
    transacoes_expandidas.sort(key=sort_key_func, reverse=(order == 'desc'))
    
    # Lógica de paginação
    total_items = len(transacoes_expandidas)
    total_pages = (total_items + per_page - 1) // per_page if per_page > 0 else 0
    start = (page - 1) * per_page
    end = start + per_page
    transacoes_paginadas = transacoes_expandidas[start:end]

    csrf_token = generate_csrf()
    transacoes_json = []
    for t in transacoes_paginadas:
        transacao_data = {
            'id': t['id'], 'descricao': t.get('descricao', ''), 'valor': float(t.get('valor', 0)), 'data': t.get('data', date.today()).strftime('%Y-%m-%d'),
            'data_formatada': t.get('data', date.today()).strftime('%d/%m/%Y'), 'tipo': t.get('tipo', ''), 'categoria_id': t.get('categoria_id', ''),
            'forma_pagamento': t.get('forma_pagamento', ''), 'recorrencia': t.get('recorrencia', ''),
            'data_final_recorrencia': t.get('data_final_recorrencia').strftime('%Y-%m-%d') if t.get('data_final_recorrencia') else None,
            'categoria_nome': t.get('categoria_nome', 'Sem Categoria'), 'is_skipped': t.get('is_skipped', False),
            'tipo_badge_class': 'text-bg-success' if t.get('tipo') == 'Receita' else 'text-bg-danger',
            'valor_formatado': format_currency(t.get('valor', 0)),
            'valor_class': 'text-success' if t.get('tipo') == 'Receita' else 'text-danger',
            'data_iso': t.get('data', date.today()).strftime('%Y-%m-%d'), 'csrf_token': csrf_token
        }
        transacoes_json.append(transacao_data)
        
    return jsonify(
        success=True, transacoes=transacoes_json,
        has_next=(page < total_pages), has_prev=(page > 1),
        next_page=(page + 1 if page < total_pages else None),
        prev_page=(page - 1 if page > 1 else None),
        current_page=page, total_pages=total_pages
    )

@main_bp.route('/transacoes/adicionar', methods=['POST'])
@login_required
def adicionar_transacao():
    form = TransacaoForm()
    form.categoria_id.choices = [(c.id, c.nome) for c in Categoria.query.filter_by(user_id=current_user.id).order_by(Categoria.nome).all()]
    if form.validate_on_submit():
        try:
            nova_transacao = Transacao(
                user_id=current_user.id, tipo=form.tipo.data, valor=parse_currency(form.valor.data),
                categoria_id=form.categoria_id.data, data=form.data.data, descricao=form.descricao.data,
                forma_pagamento=form.forma_pagamento.data or None,
                recorrencia=form.recorrencia.data if form.recorrencia_switch.data == 'on' else None,
                data_final_recorrencia=form.data_final_recorrencia.data if form.recorrencia_switch.data == 'on' and form.data_final_recorrencia.data else None
            )
            db.session.add(nova_transacao)
            db.session.commit()
            flash('Transação adicionada!', 'success')
            return jsonify(success=True, redirect_url=request.referrer or url_for('main.transacoes_redirect'))
        except Exception as e:
            db.session.rollback()
            return jsonify(success=False, errors={'geral': [f'Erro ao salvar no banco de dados: {e}']}), 500
    return jsonify(success=False, errors=form.errors), 400

@main_bp.route('/transacoes/editar/<int:id>', methods=['POST'])
@login_required
def editar_transacao(id):
    form = TransacaoForm()
    form.categoria_id.choices = [(c.id, c.nome) for c in Categoria.query.filter_by(user_id=current_user.id).order_by(Categoria.nome).all()]
    transacao = db.session.get(Transacao, id)
    if not transacao or transacao.user_id != current_user.id:
        return ('Acesso negado', 403)
    if form.validate_on_submit():
        try:
            transacao.tipo = form.tipo.data; transacao.valor = parse_currency(form.valor.data); transacao.categoria_id = form.categoria_id.data; transacao.data = form.data.data
            transacao.descricao = form.descricao.data; transacao.forma_pagamento = form.forma_pagamento.data or None
            transacao.recorrencia = form.recorrencia.data if form.recorrencia_switch.data == 'on' else None
            transacao.data_final_recorrencia = form.data_final_recorrencia.data if transacao.recorrencia else None
            db.session.commit()
            flash('Transação atualizada!', 'success')
            return jsonify(success=True, redirect_url=request.referrer or url_for('main.index'))
        except Exception as e:
            db.session.rollback()
            return jsonify(success=False, errors={'geral': [f'Erro ao salvar no banco de dados: {e}']}), 500
    return jsonify(success=False, errors=form.errors), 400
    
@main_bp.route('/transacoes/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_transacao(id):
    transacao = db.session.get(Transacao, id)
    if not transacao or transacao.user_id != current_user.id:
        return ('Acesso negado', 403)
    db.session.delete(transacao)
    db.session.commit()
    flash('Regra de transação excluída.', 'info')
    return redirect(request.referrer or url_for('main.transacoes_redirect'))

@main_bp.route('/transacoes/ignorar', methods=['POST'])
@login_required
def ignorar_ocorrencia():
    transacao_id = request.form.get('transacao_id', type=int)
    data_str = request.form.get('data_excecao')
    if not transacao_id or not data_str:
        flash('Informações inválidas para ignorar a transação.', 'danger')
        return redirect(request.referrer or url_for('main.index'))
    data_excecao = datetime.strptime(data_str, '%Y-%m-%d').date()
    regra = db.session.get(Transacao, transacao_id)
    if not regra or regra.user_id != current_user.id:
        flash('Acesso negado.', 'danger')
        return redirect(request.referrer)
    excecao_existente = ExcecaoTransacao.query.filter_by(transacao_id=transacao_id, data_excecao=data_excecao, user_id=current_user.id).first()
    if not excecao_existente:
        nova_excecao = ExcecaoTransacao(
            transacao_id=transacao_id,
            data_excecao=data_excecao,
            user_id=current_user.id
        )
        db.session.add(nova_excecao)
        db.session.commit()
        flash('Ocorrência ignorada com sucesso.', 'info')
    return redirect(request.referrer or url_for('main.transacoes_redirect'))

@main_bp.route('/transacoes/reativar', methods=['POST'])
@login_required
def reativar_ocorrencia():
    transacao_id = request.form.get('transacao_id', type=int)
    data_str = request.form.get('data_excecao')
    if not transacao_id or not data_str:
        flash('Informações inválidas para reativar a transação.', 'danger')
        return redirect(request.referrer or url_for('main.index'))
    data_excecao = datetime.strptime(data_str, '%Y-%m-%d').date()
    excecao = ExcecaoTransacao.query.filter_by(transacao_id=transacao_id, data_excecao=data_excecao, user_id=current_user.id).first()
    if excecao:
        db.session.delete(excecao)
        db.session.commit()
        flash('Ocorrência reativada com sucesso.', 'success')
    else:
        flash('Não foi possível encontrar a ocorrência para reativar.', 'warning')
    return redirect(request.referrer or url_for('main.transacoes_redirect'))

@main_bp.route('/recorrencias')
@login_required
def gerenciar_recorrencias():
    form = TransacaoForm()
    user_categories = Categoria.query.filter_by(user_id=current_user.id).order_by(Categoria.nome).all()
    regras = Transacao.query.filter(
        Transacao.user_id == current_user.id,
        Transacao.recorrencia != None
    ).order_by(Transacao.data.desc()).all()
    return render_template('main/recorrencias.html', regras=regras, form=form, user_categories=user_categories)
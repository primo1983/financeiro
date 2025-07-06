from flask import render_template, request, redirect, url_for, flash, jsonify
from . import main_bp
from app import db
from app.models import Transacao, Categoria, ExcecaoTransacao
from app.forms import TransacaoForm
from app.utils import expandir_transacoes_na_janela, parse_currency
from flask_login import login_required, current_user
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

@main_bp.route('/transacoes')
@login_required
def transacoes_redirect():
    hoje = date.today()
    return redirect(url_for('main.listar_transacoes', ano=hoje.year, mes=hoje.month))

@main_bp.route('/transacoes/<int:ano>/<int:mes>')
@login_required
def listar_transacoes(ano, mes):
    user_id = current_user.id
    form = TransacaoForm()
    user_categories = Categoria.query.filter_by(user_id=user_id).order_by(Categoria.nome).all()
    
    data_inicio_janela = date(ano, mes, 1)
    data_fim_janela = data_inicio_janela + relativedelta(months=1) - relativedelta(days=1)
    
    regras_transacoes = Transacao.query.filter_by(user_id=user_id).options(db.joinedload(Transacao.categoria)).all()
    transacoes_do_mes = expandir_transacoes_na_janela(regras_transacoes, data_inicio_janela, data_fim_janela)
    transacoes_do_mes.sort(key=lambda x: (x['data'], x['id'] if isinstance(x['id'], int) else -1), reverse=True)
    
    data_atual = date(ano, mes, 1)
    mes_anterior = data_atual - relativedelta(months=1)
    mes_seguinte = data_atual + relativedelta(months=1)
    mes_display = data_atual.strftime('%B de %Y').capitalize()
    
    return render_template('main/transacoes.html', 
        transacoes=transacoes_do_mes, form=form, user_categories=user_categories, 
        nav_mes_display=mes_display, nav_mes_anterior=mes_anterior, nav_mes_seguinte=mes_seguinte)

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
            return jsonify(success=True, redirect_url=url_for('main.listar_transacoes', ano=form.data.data.year, mes=form.data.data.month))
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
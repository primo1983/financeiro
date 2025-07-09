from flask import request, jsonify
from . import main_bp
from app import db
from app.models import Transacao
from flask_login import login_required, current_user
from sqlalchemy import func

@main_bp.route('/sugerir-dados', methods=['POST'])
@login_required
def sugerir_dados():
    """
    Recebe um texto de descrição e sugere a categoria e forma de pagamento
    mais comuns baseadas no histórico do usuário.
    """
    search_term = request.json.get('descricao')
    if not search_term or len(search_term) < 3:
        return jsonify({})

    sugestao = db.session.query(
            Transacao.categoria_id,
            Transacao.forma_pagamento,
            func.count(Transacao.id).label('frequency')
        ).filter(
            Transacao.user_id == current_user.id,
            Transacao.descricao.like(f'%{search_term}%')
        ).group_by(
            Transacao.categoria_id,
            Transacao.forma_pagamento
        ).order_by(
            func.count(Transacao.id).desc()
        ).first()

    if sugestao:
        return jsonify({
            'sugestao_categoria_id': sugestao.categoria_id,
            'sugestao_forma_pagamento': sugestao.forma_pagamento
        })

    return jsonify({})
from app import db
from flask_login import UserMixin
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash

class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    saldos_visibilidade = db.Column(db.JSON, nullable=False, default=lambda: {
        "saldo_atual": True, "receita_mes": True, 
        "despesa_mes": True, "saldo_mes": True
    })
    theme = db.Column(db.String(10), nullable=False, default='auto')
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    
    transacoes = db.relationship('Transacao', backref='usuario', lazy=True, cascade="all, delete-orphan")
    categorias = db.relationship('Categoria', backref='usuario', lazy=True, cascade="all, delete-orphan")
    excecoes_transacao = db.relationship('ExcecaoTransacao', backref='usuario', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Categoria(db.Model):
    __tablename__ = 'categorias'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    transacoes = db.relationship('Transacao', backref='categoria', lazy=True)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'nome', name='_user_id_nome_uc'),)

class Transacao(db.Model):
    __tablename__ = 'transacoes'
    
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(200), nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    data = db.Column(db.Date, nullable=False, default=date.today)
    tipo = db.Column(db.String(50), nullable=False)
    forma_pagamento = db.Column(db.String(50))
    recorrencia = db.Column(db.String(50))
    data_final_recorrencia = db.Column(db.Date)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    
    excecoes = db.relationship('ExcecaoTransacao', backref='regra_transacao', lazy=True, cascade="all, delete-orphan")

class ExcecaoTransacao(db.Model):
    __tablename__ = 'excecao_transacao'
    
    id = db.Column(db.Integer, primary_key=True)
    data_excecao = db.Column(db.Date, nullable=False)
    transacao_id = db.Column(db.Integer, db.ForeignKey('transacoes.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    __table_args__ = (db.UniqueConstraint('transacao_id', 'data_excecao', name='_transacao_data_uc'),)
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, DateField, HiddenField, RadioField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Optional, Length, InputRequired
from datetime import date

class LoginForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired("")])
    password = PasswordField('Senha', validators=[DataRequired("")])
    submit = SubmitField('Entrar')

class PerfilForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired("O e-mail é obrigatório."), Email("E-mail inválido.")])
    senha_atual = PasswordField('Senha Atual', validators=[DataRequired("Senha atual é obrigatória.")])
    nova_senha = PasswordField('Nova Senha', validators=[Optional(), Length(min=6, message="A nova senha deve ter pelo menos 6 caracteres.")])
    confirmar_senha = PasswordField('Confirmar Nova Senha', validators=[EqualTo('nova_senha', message='As senhas não correspondem.')])
    submit = SubmitField('Salvar Alterações')

class CategoriaForm(FlaskForm):
    id = HiddenField()
    nome = StringField('Nome da Categoria', validators=[DataRequired("")])
    tipo = SelectField('Tipo', choices=[('Receita', 'Receita'), ('Despesa', 'Despesa'), ('Ambos', 'Ambos')], validators=[DataRequired("")])
    submit = SubmitField('Salvar')
    
class TransacaoForm(FlaskForm):
    id = HiddenField()
    tipo = SelectField('Tipo', choices=[('Despesa', 'Despesa'), ('Receita', 'Receita')], validators=[DataRequired("")])
    categoria_id = SelectField('Categoria', coerce=int, validators=[InputRequired("")])
    valor = StringField('Valor', validators=[DataRequired("")])
    data = DateField('Data', default=date.today, validators=[DataRequired("")])
    descricao = StringField('Descrição', validators=[DataRequired("")])
    forma_pagamento = SelectField('Forma de Pgto.', choices=[('', 'N/A'), ('Pix', 'Pix'), ('Transferência', 'Transferência'), ('Boleto', 'Boleto'), ('Cartão', 'Cartão')], validators=[Optional()])
    recorrencia_switch = HiddenField()
    recorrencia = SelectField('Repetir', choices=[('Mensal', 'Mensal'), ('Quinzenal', 'Quinzenal'), ('Anual', 'Anual')], validators=[Optional()])
    data_final_recorrencia = DateField('Até (opcional)', validators=[Optional()])
    submit = SubmitField('Salvar')

class AdminUserCreateForm(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired("")])
    email = StringField('E-mail (Opcional)', validators=[Optional(), Email("E-mail inválido.")])
    password = PasswordField('Senha', validators=[DataRequired(""), Length(min=6, message="A senha deve ter pelo menos 6 caracteres.")])
    is_admin = BooleanField('Tornar Administrador?')
    submit = SubmitField('Criar Usuário')

class AdminUserEditForm(FlaskForm):
    email = StringField('E-mail (Opcional)', validators=[Optional(), Email("E-mail inválido.")])
    password = PasswordField('Nova Senha (deixe em branco para não alterar)', validators=[Optional(), Length(min=6, message="A senha deve ter pelo menos 6 caracteres.")])
    is_admin = BooleanField('É Administrador?')
    submit = SubmitField('Salvar Alterações')
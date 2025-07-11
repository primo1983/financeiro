from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, DateField, HiddenField, RadioField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Optional, Length
from datetime import date

class LoginForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired("Este campo é obrigatório.")])
    password = PasswordField('Senha', validators=[DataRequired("Este campo é obrigatório.")])
    # --- CAMPO ADICIONADO AQUI ---
    remember_me = BooleanField('Lembrar-me')
    submit = SubmitField('Entrar')

class PerfilForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired("O e-mail é obrigatório."), Email("E-mail inválido.")])
    theme = RadioField('Tema', choices=[('auto', 'Sistema'), ('light', 'Claro'), ('dark', 'Escuro')], default='auto')
    senha_atual = PasswordField('Senha Atual', validators=[DataRequired("Senha atual é obrigatória para salvar.")])
    nova_senha = PasswordField('Nova Senha', validators=[Optional(), Length(min=6, message="A nova senha deve ter pelo menos 6 caracteres.")])
    confirmar_senha = PasswordField('Confirmar Nova Senha', validators=[EqualTo('nova_senha', message='As senhas não correspondem.')])
    submit = SubmitField('Salvar Alterações')

class CategoriaForm(FlaskForm):
    id = HiddenField()
    nome = StringField('Nome da Categoria', validators=[DataRequired("O nome é obrigatório.")])
    tipo = SelectField('Tipo', choices=[('Receita', 'Receita'), ('Despesa', 'Despesa'), ('Ambos', 'Ambos')], validators=[DataRequired("O tipo é obrigatório.")])
    submit = SubmitField('Salvar')
    
class TransacaoForm(FlaskForm):
    id = HiddenField()
    tipo = SelectField('Tipo', choices=[('Despesa', 'Despesa'), ('Receita', 'Receita')], validators=[DataRequired("O tipo é obrigatório.")])
    categoria_id = SelectField('Categoria', coerce=int, validators=[DataRequired("Por favor, selecione uma categoria.")])
    valor = StringField('Valor', validators=[DataRequired("O valor é obrigatório.")])
    data = DateField('Data', default=date.today, validators=[DataRequired("A data é obrigatória.")])
    descricao = StringField('Descrição', validators=[DataRequired("A descrição é obrigatória.")])
    
    forma_pagamento = SelectField('Forma de Pgto.', choices=[('', 'N/A'), ('Pix', 'Pix'), ('Transferência', 'Transferência'), ('Boleto', 'Boleto'), ('Cartão', 'Cartão')], validators=[Optional()])
    recorrencia_switch = HiddenField()
    recorrencia = SelectField('Repetir', choices=[('Mensal', 'Mensal'), ('Quinzenal', 'Quinzenal'), ('Anual', 'Anual')], validators=[Optional()])
    data_final_recorrencia = DateField('Até (opcional)', validators=[Optional()])
    submit = SubmitField('Salvar')

class AdminUserCreateForm(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired("O nome de usuário é obrigatório.")])
    email = StringField('E-mail (Opcional)', validators=[Optional(), Email("E-mail inválido.")])
    password = PasswordField('Senha', validators=[DataRequired("A senha é obrigatória."), Length(min=6, message="A senha deve ter pelo menos 6 caracteres.")])
    is_admin = BooleanField('Tornar Administrador?')
    submit = SubmitField('Criar Usuário')

class AdminUserEditForm(FlaskForm):
    email = StringField('E-mail (Opcional)', validators=[Optional(), Email("E-mail inválido.")])
    password = PasswordField('Nova Senha (deixe em branco para não alterar)', validators=[Optional(), Length(min=6, message="A senha deve ter pelo menos 6 caracteres.")])
    is_admin = BooleanField('É Administrador?')
    submit = SubmitField('Salvar Alterações')
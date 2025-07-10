import os
import locale
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from flask_migrate import Migrate
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
csrf = CSRFProtect()
login_manager = LoginManager()
migrate = Migrate()
login_manager.login_view = 'auth.login'
login_manager.login_message = "Por favor, faça login para acessar esta página."
login_manager.login_message_category = "warning"

def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URI'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )
    
    # O locale pode ser configurado uma vez aqui.
    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
        except locale.Error:
            print("Atenção: Não foi possível definir o locale para pt_BR. A formatação de moeda pode não funcionar como esperado.")

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        from . import models
        @login_manager.user_loader
        def load_user(user_id):
            return db.session.get(models.Usuario, int(user_id))

        from .auth import auth_bp
        app.register_blueprint(auth_bp)
        
        from .main import main_bp
        app.register_blueprint(main_bp)

        from . import commands
        commands.register_commands(app)
        
        # --- CORREÇÃO APLICADA AQUI ---
        # Importamos o nosso módulo de utilitários
        from . import utils
        # E registamos a função como um filtro para os templates.
        app.jinja_env.filters['currency'] = utils.format_currency

    return app
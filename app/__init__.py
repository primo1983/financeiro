import os
import locale
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from flask_migrate import Migrate
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
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
    
    # MUDANÇA: Configurações agora são lidas das variáveis de ambiente
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URI'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )
    
    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    except locale.Error:
        locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
    
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
        from . import utils

    return app
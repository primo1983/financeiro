import locale
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from flask_migrate import Migrate

# Inicializa as extensões globalmente
db = SQLAlchemy()
csrf = CSRFProtect()
login_manager = LoginManager()
migrate = Migrate()

# Configura o redirecionamento para a página de login
login_manager.login_view = 'auth.login'
login_manager.login_message = "Por favor, faça login para acessar esta página."
login_manager.login_message_category = "warning"

def create_app():
    """Cria e configura uma instância da aplicação Flask."""
    
    app = Flask(__name__)
    
    # --- CONFIGURAÇÃO ---
    app.config.from_mapping(
        SECRET_KEY='uma-chave-secreta-muito-forte-e-diferente-para-producao',
        SQLALCHEMY_DATABASE_URI=f"mysql+mysqlconnector://root:teste@localhost/financas",
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )

    # Configura o locale para o formato de moeda brasileiro
    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    except locale.Error:
        locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
    
    # --- INICIALIZA EXTENSÕES COM O APP ---
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        from . import models

        @login_manager.user_loader
        def load_user(user_id):
            return db.session.get(models.Usuario, int(user_id))

        # --- REGISTRO DOS BLUEPRINTS ---
        from .auth import auth_bp
        app.register_blueprint(auth_bp)

        from .main import main_bp
        app.register_blueprint(main_bp)

        # Importa e registra os comandos de terminal
        from . import commands
        commands.register_commands(app)
        
        # Importa e registra os filtros de template
        from . import utils

    return app
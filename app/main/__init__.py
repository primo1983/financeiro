from flask import Blueprint

main_bp = Blueprint('main', __name__)

# Importa todos os arquivos de rotas para registrá-las no blueprint
from . import routes_core, routes_transacoes, routes_categorias, routes_admin, routes_analises, routes_api
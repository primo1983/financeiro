from flask import Blueprint

main_bp = Blueprint('main', __name__)

# As importações de rotas vêm DEPOIS da definição do blueprint para evitar importação circular.
from . import routes_core
from . import routes_transacoes
from . import routes_categorias
from . import routes_admin
from . import routes_analises
from . import routes_api
from flask import Blueprint

auth_bp = Blueprint('auth', __name__)

# A importação das rotas vem DEPOIS da definição do blueprint.
from . import routes
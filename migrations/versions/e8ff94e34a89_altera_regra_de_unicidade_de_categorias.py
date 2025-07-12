"""Altera regra de unicidade para categorias

Revision ID: e8ff94e34a89
Revises: 7096947caf50
Create Date: 2025-07-10 12:34:56.789012

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'e8ff94e34a89'
down_revision = '7096947caf50' # O ID da sua revisão anterior estará aqui
branch_labels = None
depends_on = None


def upgrade():
    # ### Usando o modo "batch" para lidar com as restrições do SQLite/MySQL ###
    with op.batch_alter_table('categorias', schema=None) as batch_op:
        # Primeiro, criamos a nova regra
        batch_op.create_unique_constraint('_user_id_nome_tipo_uc', ['user_id', 'nome', 'tipo'])
        # Depois, apagamos a regra antiga
        batch_op.drop_constraint('_user_id_nome_uc', type_='unique')

    # ### end Alembic commands ###


def downgrade():
    # ### A operação inversa, também em modo "batch" ###
    with op.batch_alter_table('categorias', schema=None) as batch_op:
        # Primeiro, recriamos a regra antiga
        batch_op.create_unique_constraint('_user_id_nome_uc', ['user_id', 'nome'])
        # Depois, apagamos a regra nova
        batch_op.drop_constraint('_user_id_nome_tipo_uc', type_='unique')

    # ### end Alembic commands ###
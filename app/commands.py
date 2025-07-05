import click
from app import db
from app.models import Usuario, Categoria
from werkzeug.security import generate_password_hash

def register_commands(app):
    @app.cli.command("db-create")
    def db_create():
        """Cria todas as tabelas do banco de dados."""
        db.create_all()
        print("Banco de dados e tabelas criados com sucesso!")

    @app.cli.command("db-seed")
    def db_seed():
        """Popula o banco com um usuário admin e categorias iniciais."""
        if Usuario.query.filter_by(username='admin').first():
            print("Usuário 'admin' já existe.")
        else:
            # MUDANÇA: O usuário 'admin' agora é criado com is_admin=True
            admin_user = Usuario(username='admin', password=generate_password_hash('password'), email='admin@example.com', is_admin=True)
            db.session.add(admin_user)
            db.session.commit()
            print("Usuário 'admin' criado com privilégios de administrador.")

            if not admin_user.categorias:
                categorias_iniciais = [
                    Categoria(user_id=admin_user.id, nome='Salário', tipo='Receita'),
                    Categoria(user_id=admin_user.id, nome='Moradia', tipo='Despesa'),
                    Categoria(user_id=admin_user.id, nome='Alimentação', tipo='Despesa'),
                ]
                db.session.bulk_save_objects(categorias_iniciais)
                db.session.commit()
                print("Categorias iniciais para o usuário 'admin' criadas.")

    @app.cli.command("create-user")
    @click.argument("username")
    @click.argument("password")
    @click.option("--email", default=None, help="O e-mail do usuário.")
    @click.option("--admin", is_flag=True, help="Define o usuário como administrador.")
    def create_user(username, password, email, admin):
        """Cria um novo usuário."""
        if not username or not password:
            print("Erro: Nome de usuário e senha são obrigatórios.")
            return
        if Usuario.query.filter_by(username=username).first():
            print(f"Erro: Usuário '{username}' já existe.")
            return
        novo_usuario = Usuario(username=username, password=generate_password_hash(password), email=email, is_admin=admin)
        db.session.add(novo_usuario)
        db.session.commit()
        if admin:
            print(f"Usuário administrador '{username}' criado com sucesso!")
        else:
            print(f"Usuário '{username}' criado com sucesso!")
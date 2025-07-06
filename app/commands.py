import click
from app import db
from app.models import Usuario, Categoria
from werkzeug.security import generate_password_hash

def register_commands(app):
    @app.cli.command("db-seed")
    def db_seed():
        if Usuario.query.filter_by(username='admin').first():
            print("Usuário 'admin' já existe.")
        else:
            admin_user = Usuario(username='admin', email='admin@example.com', is_admin=True)
            admin_user.set_password('password')
            db.session.add(admin_user)
            db.session.commit()
            print("Usuário 'admin' criado com privilégios de administrador.")
            if not admin_user.categorias:
                categorias_iniciais = [ Categoria(user_id=admin_user.id, nome='Salário', tipo='Receita'), Categoria(user_id=admin_user.id, nome='Moradia', tipo='Despesa'), Categoria(user_id=admin_user.id, nome='Alimentação', tipo='Despesa')]
                db.session.bulk_save_objects(categorias_iniciais)
                db.session.commit()
                print("Categorias iniciais para o usuário 'admin' criadas.")

    @app.cli.command("create-user")
    @click.argument("username")
    @click.argument("password")
    @click.option("--email", default=None, help="O e-mail do usuário.")
    @click.option("--admin", is_flag=True, help="Define o usuário como administrador.")
    def create_user(username, password, email, admin):
        if not username or not password: print("Erro: Nome de usuário e senha são obrigatórios."); return
        if Usuario.query.filter_by(username=username).first(): print(f"Erro: Usuário '{username}' já existe."); return
        novo_usuario = Usuario(username=username, email=email, is_admin=admin)
        novo_usuario.set_password(password)
        db.session.add(novo_usuario); db.session.commit()
        print(f"Usuário '{'administrador ' if admin else ''}{username}' criado com sucesso!")

    # --- NOVO COMANDO ---
    @app.cli.command("reset-password")
    @click.argument("username")
    @click.argument("new_password")
    def reset_password(username, new_password):
        """Redefine a senha de um usuário existente."""
        user = Usuario.query.filter_by(username=username).first()
        if user:
            user.set_password(new_password)
            db.session.commit()
            print(f"Senha para o usuário '{username}' foi redefinida com sucesso.")
        else:
            print(f"Usuário '{username}' não encontrado.")
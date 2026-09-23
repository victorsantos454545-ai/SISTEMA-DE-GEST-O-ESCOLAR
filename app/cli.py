"""Comandos CLI do Flask para administracao do sistema."""
import click
from flask.cli import with_appcontext
from app.extensions import db


def register_commands(app):
    """Registra todos os comandos CLI."""
    app.cli.add_command(create_admin_cmd)
    app.cli.add_command(seed_permissions_cmd)


@click.command('create-admin')
@click.option('--username', prompt='Username', help='Nome de usuario do admin')
@click.option('--email', prompt='E-mail', help='E-mail do admin')
@click.option('--password', prompt=True, hide_input=True,
              confirmation_prompt=True, help='Senha do admin')
@with_appcontext
def create_admin_cmd(username, email, password):
    """Cria o usuario administrador."""
    from app.models.user import User
    from app.models.role import Role

    if len(password) < 10:
        click.echo('Erro: A senha deve ter no minimo 10 caracteres.')
        return

    admin_role = Role.query.filter_by(name='admin').first()
    if admin_role is None:
        click.echo('Erro: Role "admin" nao encontrada. Execute seed de permissoes primeiro.')
        click.echo('  flask seed-permissions')
        return

    if User.query.filter_by(username=username).first():
        click.echo(f'Erro: Username "{username}" ja existe.')
        return

    if User.query.filter_by(email=email).first():
        click.echo(f'Erro: E-mail "{email}" ja cadastrado.')
        return

    user = User(
        username=username,
        email=email,
        role_id=admin_role.id,
        active=True,
        must_change_password=False
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    click.echo(f'Admin "{username}" criado com sucesso!')


@click.command('seed-permissions')
@with_appcontext
def seed_permissions_cmd():
    """Popula roles e permissoes do sistema (idempotente)."""
    from app.services.seed_service import seed_all_permissions
    seed_all_permissions()
    click.echo('Seed de permissoes concluida!')

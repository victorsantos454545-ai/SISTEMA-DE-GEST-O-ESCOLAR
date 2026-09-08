# Arquitetura do Sistema

## Padrão Utilizado
O Sistema de Gestão Escolar (SGE) utiliza a arquitetura MVC (Model-View-Controller) implementada sob o framework Flask no padrão Application Factory, o que garante modularidade e testes isolados.

## Fluxo da Aplicação
Usuário -> Rota (Blueprints) -> Autenticação/Autorização (Flask-Login & RBAC) -> Formulário (WTForms) -> Service (Regras de Negócio) -> SQLAlchemy (ORM) -> Banco de Dados -> Resposta (Jinja2 Templates).

## Estrutura
- **models/**: Definições das tabelas e relacionamentos.
- **routes/**: Controladores (Blueprints) que lidam com as requisições HTTP.
- **services/**: Camada de serviço onde a lógica de negócio pesada (ex: fechamento de notas) reside.
- **forms/**: Validação de dados de entrada com WTForms.
- **templates/** e **static/**: Camada de visão usando Jinja2 e Bootstrap 5.

## Onde adicionar novos recursos
- Nova rota: `app/routes/` e registrar no `app/__init__.py`.
- Nova regra: `app/services/`.
- Novo modelo: `app/models/` e expor em `app/models/__init__.py`.
- Novos testes: `tests/`.

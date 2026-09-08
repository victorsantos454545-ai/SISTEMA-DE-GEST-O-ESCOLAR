# Documentação de Segurança

*Aviso: Esta documentação descreve as medidas implementadas e não constitui garantia de segurança absoluta.*

- **Hash de Senha**: Usado `generate_password_hash` (PBKDF2).
- **Força Bruta**: Bloqueio de 15 min após 5 falhas no serviço de auth.
- **Proteção CSRF**: Ativada globalmente via `Flask-WTF` (`csrf.init_app(app)`).
- **SQL Injection**: Prevenido pela exclusividade de uso do SQLAlchemy ORM. Não há `execute()` bruto iterativo.
- **XSS**: Templates utilizam Jinja2 com auto-escape ativo. A tag `|safe` não é exposta a inputs de usuário.
- **Object-Level Authorization (IDOR)**: Rotas sensíveis validam `can_access_student(user, id)` para evitar injeções pela URL.
- **Mass Assignment**: Lançamentos em lote (Notas/Faltas) validam as matrículas ativas da turma antes de salvar.
- **Headers HTTP**: Injetados em `__init__.py` (`X-Frame-Options`, `X-Content-Type-Options`, `Strict-Transport-Security`).

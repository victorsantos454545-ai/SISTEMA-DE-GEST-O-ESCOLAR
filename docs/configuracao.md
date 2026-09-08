# Documentação de Configuração

O sistema utiliza variáveis de ambiente (`.env`) lidas pelo pacote `python-dotenv` em `config.py`.

## Variáveis Principais

- `FLASK_ENV`: Define o ambiente (`development`, `production`, `testing`).
- `FLASK_DEBUG`: `1` para dev, `0` para produção.
- `SECRET_KEY`: Usada para assinar os cookies de sessão. Exemplo: `change-this-secret`. NUNCA use valores reais no repositório.
- `DATABASE_URL`: URI do banco. Exemplo: `sqlite:///instance/school.db`.
- `SCHOOL_NAME`: Nome da instituição.
- `SCHOOL_ABBREVIATION`: Sigla.
- `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USE_TLS`, `MAIL_USERNAME`, `MAIL_PASSWORD`: Configuração do servidor SMTP.
- `MAX_LOGIN_ATTEMPTS`: Limite contra força bruta (ex: 5).
- `LOCKOUT_DURATION_MINUTES`: Tempo de bloqueio (ex: 15).

# Deploy

Para publicar em produção, atente-se às seguintes configurações obrigatórias no servidor (ex: Ubuntu VPS, Heroku, AWS):

1. **Variáveis Críticas**:
   - `FLASK_ENV=production`
   - `FLASK_DEBUG=0`
   - `SECRET_KEY` forte gerada por `secrets.token_hex(32)`.
   - `DATABASE_URL` apontando para o MySQL/PostgreSQL gerido.
2. **Servidor WSGI**:
   - O Gunicorn foi adicionado às requirements.
   - Comando: `gunicorn -w 4 -b 127.0.0.1:8000 "app:create_app()"`
3. **Proxy Reverso**:
   - Nginx ou Apache fornecendo certificado SSL (HTTPS).
4. **Segurança de Cookies**:
   - Com o HTTPS ativo, descomente `SESSION_COOKIE_SECURE=true` no `.env`.

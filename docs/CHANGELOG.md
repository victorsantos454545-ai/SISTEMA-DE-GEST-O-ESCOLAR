# Changelog

## [v1.0.0] - Lançamento

### Adicionado
- Arquitetura Application Factory e MVC.
- Painéis independentes para 5 Perfis de Acesso (RBAC).
- Lançamento de Notas e Faltas (em lote).
- Dashboards com gráficos dinâmicos via Chart.js.
- Geração de Boletins Escolares completos.
- Envio de comunicados segmentados.
- Testes end-to-end com Pytest.
- GitHub Actions CI de integração contínua.

### Segurança
- Object-Level Authorization (IDOR Shield) nas notas, faltas e relatórios.
- Flask-WTF CSRF Ativado.
- Proteção nativa contra Mass Assignment.

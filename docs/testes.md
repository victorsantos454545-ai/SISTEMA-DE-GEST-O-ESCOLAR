# Documentação de Testes

Os testes são automatizados usando o `pytest` nativo em memória.

## Estrutura
- `conftest.py`: Fixtures (`seeded_app`, `client`, `admin_user`).
- `test_app.py`: Testes de inicialização.
- `test_academic.py`: Regras de negócio de matrículas e notas.
- `test_attendance.py`: Regras de presença.
- `test_reports.py`: Validação RBAC nos boletins.
- `test_regression.py`: Teste E2E (Fim a fim) validando a escola inteira funcionando integrada.
- `test_security.py` (dentro dos módulos): IDOR e CSRF.

## Execução
```bash
# Rodar todos os 75 testes
pytest

# Rodar com print das saídas
pytest -s

# Verbosidade
pytest -v
```
